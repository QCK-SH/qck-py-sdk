"""Low-level HTTP client with authentication, retries, and error mapping.

This module provides the :class:`HttpClient` class, which is the sole
transport layer used by every resource class in the SDK. It handles:

* Automatic ``X-API-Key`` header injection for authentication.
* Exponential back-off retries on transient failures (rate limits,
  connection errors, and timeouts).
* Mapping HTTP error responses to typed SDK exceptions
  (:class:`~qck._errors.ValidationError`, :class:`~qck._errors.AuthenticationError`,
  :class:`~qck._errors.NotFoundError`, :class:`~qck._errors.RateLimitError`).
* Unwrapping the standard ``{"success", "data", "error", "meta"}`` API
  envelope, including flat middleware errors
  (``{"success": false, "error": "CODE", "message": "..."}``) and
  pagination metadata carried in ``meta``.

End users should not need to instantiate :class:`HttpClient` directly;
the :class:`~qck.QCK` constructor creates one internally.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional, TypeVar

import httpx

from ._errors import (
    AuthenticationError,
    NotFoundError,
    QCKError,
    RateLimitError,
    ValidationError,
)

T = TypeVar("T")

_DEFAULT_BASE_URL = "https://qck.sh/public-api/v1"
_DEFAULT_TIMEOUT = 30
_DEFAULT_RETRIES = 3
_MAX_RETRY_DELAY = 120


class HttpClient:
    """HTTP client that handles auth, retries, and error mapping for the QCK API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = _DEFAULT_TIMEOUT,
        retries: int = _DEFAULT_RETRIES,
    ) -> None:
        """Create a new HTTP client.

        Args:
            api_key: QCK API key used for the ``X-API-Key`` header.
            base_url: API base URL. A trailing slash is stripped
                automatically.
            timeout: Request timeout in seconds.
            retries: Maximum number of retry attempts for transient
                failures.
        """
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retries = retries
        self._client = httpx.Client(
            timeout=httpx.Timeout(timeout),
            headers={
                "X-API-Key": api_key,
                "Accept": "application/json",
            },
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "HttpClient":
        """Enter the context manager, returning the client instance."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit the context manager, closing the HTTP session."""
        self.close()

    # ----- public methods -----

    def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Send a GET request.

        Args:
            path: API path (e.g. ``/links``).
            params: Optional query-string parameters.

        Returns:
            Parsed JSON response data (envelope unwrapped).

        Raises:
            QCKError: On any API error response.
        """
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        body: Any = None,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Send a POST request with an optional JSON body.

        Args:
            path: API path (e.g. ``/links``).
            body: Request body serialised as JSON.
            params: Optional query-string parameters.
            headers: Optional extra HTTP headers.

        Returns:
            Parsed JSON response data (envelope unwrapped).

        Raises:
            QCKError: On any API error response.
        """
        return self._request("POST", path, json=body, params=params, headers=headers)

    def patch(
        self,
        path: str,
        body: Any = None,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Send a PATCH request with an optional JSON body.

        Args:
            path: API path (e.g. ``/links/{id}``).
            body: Fields to update, serialised as JSON.
            params: Optional query-string parameters.

        Returns:
            Parsed JSON response data (envelope unwrapped).

        Raises:
            QCKError: On any API error response.
        """
        return self._request("PATCH", path, json=body, params=params)

    def put(
        self,
        path: str,
        body: Any = None,
        *,
        params: Optional[Dict[str, Any]] = None,
        content: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Send a PUT request with a JSON body or raw bytes.

        When *content* is provided, it is sent as the raw request body
        and *body* is ignored. This is used for binary uploads (e.g.
        OG images).

        Args:
            path: API path (e.g. ``/links/{id}/og-image``).
            body: Request body serialised as JSON (ignored when
                *content* is set).
            params: Optional query-string parameters.
            content: Raw bytes to send as the request body.
            headers: Extra headers merged into the request (e.g.
                ``Content-Type`` for binary uploads).

        Returns:
            Parsed JSON response data (envelope unwrapped).

        Raises:
            QCKError: On any API error response.
        """
        return self._request(
            "PUT", path, json=body, params=params, content=content, headers=headers,
        )

    def delete(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Send a DELETE request.

        Args:
            path: API path (e.g. ``/links/{id}``).
            params: Optional query-string parameters.

        Returns:
            ``None`` for 204 responses, or parsed JSON data otherwise.

        Raises:
            QCKError: On any API error response.
        """
        return self._request("DELETE", path, params=params)

    # ----- internals -----

    def _build_url(self, path: str) -> str:
        """Combine the base URL with an API path.

        Args:
            path: Relative API path starting with ``/``.

        Returns:
            Fully qualified URL string.
        """
        return f"{self._base_url}{path}"

    @staticmethod
    def _clean_params(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Strip ``None`` values and stringify params for query strings.

        Booleans are lowered (``True`` -> ``"true"``), lists are kept
        as-is for multi-value params, and all other values are cast to
        ``str``.

        Args:
            params: Raw parameter dictionary (may contain ``None`` values).

        Returns:
            A cleaned dictionary ready for ``httpx``, or ``None`` if empty.
        """
        if not params:
            return None
        cleaned: Dict[str, Any] = {}
        for k, v in params.items():
            if v is None:
                continue
            if isinstance(v, list):
                cleaned[k] = v
            elif isinstance(v, bool):
                cleaned[k] = str(v).lower()
            else:
                cleaned[k] = str(v)
        return cleaned or None

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: Optional[Dict[str, Any]] = None,
        content: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Execute an HTTP request with automatic retries.

        Rate limits (:class:`~qck._errors.RateLimitError`, honouring
        ``Retry-After``) are retried for every request. Network errors
        (``httpx.TimeoutException``, ``httpx.ConnectError``) are retried
        only for idempotent requests — ``GET`` requests, or requests
        carrying an ``X-Idempotency-Key`` header. A timed-out plain
        ``POST`` is *not* retried, because the server may already have
        processed it.

        Args:
            method: HTTP method (``GET``, ``POST``, etc.).
            path: Relative API path.
            json: Body to serialise as JSON (ignored when *content*
                is provided).
            params: Query-string parameters.
            content: Raw bytes body (for binary uploads).
            headers: Extra request headers.

        Returns:
            Parsed and envelope-unwrapped response data.

        Raises:
            RateLimitError: If rate-limited after all retries exhausted.
            QCKError: On non-retryable API errors.
        """
        url = self._build_url(path)
        clean = self._clean_params(params)
        idempotent = method == "GET" or bool(headers and headers.get("X-Idempotency-Key"))
        last_exc: Optional[Exception] = None

        for attempt in range(self._retries + 1):
            try:
                resp = self._client.request(
                    method,
                    url,
                    json=json if content is None else None,
                    content=content,
                    params=clean,
                    headers=headers,
                )
                return self._handle_response(resp)
            except (RateLimitError, httpx.TimeoutException, httpx.ConnectError) as exc:
                last_exc = exc
                retryable = isinstance(exc, RateLimitError) or idempotent
                if not retryable or attempt >= self._retries:
                    raise
                delay = self._retry_delay(exc, attempt)
                time.sleep(delay)

        raise last_exc  # type: ignore[misc]

    def _handle_response(self, resp: httpx.Response) -> Any:
        """Process an HTTP response, raising on errors.

        Handles, in order:

        * **429** — raises :class:`~qck._errors.RateLimitError` with the
          ``Retry-After`` header and the API's message/code when present.
        * **Empty body** — for 204 / zero-length bodies, raises a typed
          exception when the status is an error, otherwise returns ``None``.
        * **Standard envelope** ``{"success", "data", "error", "meta"}`` —
          on success, returns ``data``; when ``meta`` carries pagination,
          returns ``{"data", "page", "per_page", "total", "total_pages"}``.
        * **Flat middleware errors** ``{"success": false, "error": "CODE",
          "message": "..."}`` — raised with the real code attached.
        * **Bulk partial results** (207/422) — ``success: false`` with
          ``data`` present returns the data instead of raising, so callers
          receive the ``BulkCreateResult`` with per-item failures.

        Args:
            resp: The ``httpx.Response`` to process.

        Returns:
            The unwrapped response data.

        Raises:
            RateLimitError: On HTTP 429 responses.
            QCKError: On error responses or undecodable bodies.
        """
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "60"))
            retry_after = min(retry_after, _MAX_RETRY_DELAY)
            message = "Rate limit exceeded"
            code = "RATE_LIMIT_EXCEEDED"
            try:
                body = resp.json()
            except Exception:
                body = None
            if isinstance(body, dict):
                message = body.get("message") or message
                err = body.get("error")
                if isinstance(err, str) and err:
                    code = err
                elif isinstance(err, dict):
                    code = err.get("code") or code
                    message = err.get("message") or message
            raise RateLimitError(message=message, retry_after=retry_after, code=code)

        empty_body = resp.status_code == 204 or resp.headers.get("content-length") == "0"
        if empty_body:
            if resp.status_code >= 400:
                self._raise_error(
                    resp.status_code, "UNKNOWN", resp.text or f"HTTP {resp.status_code}"
                )
            return None

        try:
            body = resp.json()
        except Exception as exc:
            if resp.status_code >= 400:
                self._raise_error(
                    resp.status_code, "UNKNOWN", resp.text or f"HTTP {resp.status_code}"
                )
            raise QCKError(
                f"Failed to decode JSON response: {exc}",
                resp.status_code,
                "INVALID_RESPONSE",
            ) from exc

        if isinstance(body, dict) and "success" in body:
            if not body.get("success"):
                # Bulk 207/422: partial-success responses carry the result
                # data alongside success=false. Return it instead of raising.
                if body.get("data") is not None:
                    return body.get("data")

                err = body.get("error")
                if isinstance(err, str):
                    # Flat middleware error: {"error": "CODE", "message": "..."}
                    code = err or "UNKNOWN"
                    message = body.get("message") or "Unknown error"
                elif isinstance(err, dict):
                    code = err.get("code") or "UNKNOWN"
                    message = err.get("message") or "Unknown error"
                else:
                    code = "UNKNOWN"
                    message = body.get("message") or "Unknown error"
                self._raise_error(resp.status_code, code, message)

            meta = body.get("meta")
            data = body.get("data")
            if isinstance(meta, dict) and meta.get("page") is not None:
                return {
                    "data": data,
                    "page": meta.get("page"),
                    "per_page": meta.get("per_page"),
                    "total": meta.get("total"),
                    "total_pages": meta.get("total_pages"),
                }
            return data

        if resp.status_code >= 400:
            self._raise_error(resp.status_code, "UNKNOWN", resp.text)

        return body

    @staticmethod
    def _raise_error(status: int, code: str, message: str) -> None:
        """Raise the typed SDK exception for an error status.

        Maps HTTP status codes to the appropriate exception class while
        preserving the API's machine-readable error code:

        * 400 -> :class:`~qck._errors.ValidationError`
        * 401 -> :class:`~qck._errors.AuthenticationError`
        * 404 -> :class:`~qck._errors.NotFoundError`
        * Other -> :class:`~qck._errors.QCKError`

        Args:
            status: HTTP status code.
            code: Machine-readable error code from the API response.
            message: Human-readable error description.

        Raises:
            ValidationError: On HTTP 400.
            AuthenticationError: On HTTP 401.
            NotFoundError: On HTTP 404.
            QCKError: On all other error status codes.
        """
        if status == 400:
            raise ValidationError(message, code=code)
        if status == 401:
            raise AuthenticationError(message, code=code)
        if status == 404:
            raise NotFoundError(message, code=code)
        raise QCKError(message, status, code)

    @staticmethod
    def _retry_delay(exc: Exception, attempt: int) -> float:
        """Calculate the delay before the next retry attempt.

        For :class:`~qck._errors.RateLimitError`, the ``Retry-After``
        header value is used (capped at :data:`_MAX_RETRY_DELAY`).
        For other transient errors, exponential back-off is applied
        (``2 ** attempt``, capped at 10 seconds).

        Args:
            exc: The exception that triggered the retry.
            attempt: Zero-based attempt counter.

        Returns:
            Number of seconds to sleep before retrying.
        """
        if isinstance(exc, RateLimitError):
            return min(exc.retry_after, _MAX_RETRY_DELAY)
        base = min(2**attempt, 10)
        return float(base)
