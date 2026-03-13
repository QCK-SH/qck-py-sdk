"""Low-level HTTP client with authentication, retries, and error mapping.

This module provides the :class:`HttpClient` class, which is the sole
transport layer used by every resource class in the SDK. It handles:

* Automatic ``X-API-Key`` header injection for authentication.
* Exponential back-off retries on transient failures (rate limits,
  connection errors, and timeouts).
* Mapping HTTP error responses to typed SDK exceptions
  (:class:`~qck._errors.ValidationError`, :class:`~qck._errors.AuthenticationError`,
  :class:`~qck._errors.NotFoundError`, :class:`~qck._errors.RateLimitError`).
* Unwrapping the standard ``{"success": bool, "data": ...}`` API envelope.

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

_DEFAULT_BASE_URL = "https://api.qck.sh/public-api/v1"
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
    ) -> Any:
        """Send a POST request with an optional JSON body.

        Args:
            path: API path (e.g. ``/links``).
            body: Request body serialised as JSON.
            params: Optional query-string parameters.

        Returns:
            Parsed JSON response data (envelope unwrapped).

        Raises:
            QCKError: On any API error response.
        """
        return self._request("POST", path, json=body, params=params)

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

        Retries are triggered by :class:`~qck._errors.RateLimitError`,
        ``httpx.TimeoutException``, and ``httpx.ConnectError``. The
        delay between attempts is determined by :meth:`_retry_delay`.

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
                return self._handle_response(resp, attempt)
            except (RateLimitError, httpx.TimeoutException, httpx.ConnectError) as exc:
                last_exc = exc
                if attempt >= self._retries:
                    raise
                delay = self._retry_delay(exc, attempt)
                time.sleep(delay)

        raise last_exc  # type: ignore[misc]

    def _handle_response(self, resp: httpx.Response, attempt: int) -> Any:
        """Process an HTTP response, raising on errors.

        Handles 429 (rate limit), 204 / empty-body (returns ``None``),
        and the standard ``{"success": bool, "data": ...}`` envelope.

        Args:
            resp: The ``httpx.Response`` to process.
            attempt: Current retry attempt number (0-based).

        Returns:
            The ``data`` field from the API envelope, or the raw parsed
            JSON if the response is not wrapped in the standard envelope.

        Raises:
            RateLimitError: On HTTP 429 responses.
            QCKError: When the envelope indicates ``success: false``.
        """
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "60"))
            retry_after = min(retry_after, _MAX_RETRY_DELAY)
            raise RateLimitError(
                message="Rate limit exceeded",
                retry_after=retry_after,
            )

        if resp.status_code == 204 or resp.headers.get("content-length") == "0":
            return None

        self._raise_for_status(resp)

        body = resp.json()

        if isinstance(body, dict) and "success" in body:
            if not body.get("success"):
                err = body.get("error", {})
                raise QCKError(
                    message=err.get("message", "Unknown error"),
                    status=resp.status_code,
                    code=err.get("code", "UNKNOWN"),
                )
            return body.get("data")

        return body

    @staticmethod
    def _raise_for_status(resp: httpx.Response) -> None:
        """Raise a typed SDK exception for 4xx/5xx responses.

        Maps HTTP status codes to the appropriate exception class:

        * 400 -> :class:`~qck._errors.ValidationError`
        * 401 -> :class:`~qck._errors.AuthenticationError`
        * 404 -> :class:`~qck._errors.NotFoundError`
        * Other 4xx/5xx -> :class:`~qck._errors.QCKError`

        Args:
            resp: The ``httpx.Response`` to inspect.

        Raises:
            ValidationError: On HTTP 400.
            AuthenticationError: On HTTP 401.
            NotFoundError: On HTTP 404.
            QCKError: On all other error status codes.
        """
        if resp.status_code < 400:
            return

        try:
            body = resp.json()
            msg = body.get("error", {}).get("message", resp.text)
            code = body.get("error", {}).get("code", "UNKNOWN")
        except Exception:
            msg = resp.text
            code = "UNKNOWN"

        if resp.status_code == 400:
            raise ValidationError(msg)
        if resp.status_code == 401:
            raise AuthenticationError(msg)
        if resp.status_code == 404:
            raise NotFoundError(msg)

        raise QCKError(msg, resp.status_code, code)

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
