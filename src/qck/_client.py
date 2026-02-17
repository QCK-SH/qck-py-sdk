"""Low-level HTTP client with authentication, retries, and error mapping."""

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
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ----- public methods -----

    def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        body: Any = None,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self._request("POST", path, json=body, params=params)

    def patch(
        self,
        path: str,
        body: Any = None,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self._request("PATCH", path, json=body, params=params)

    def delete(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self._request("DELETE", path, params=params)

    # ----- internals -----

    def _build_url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    @staticmethod
    def _clean_params(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        if not params:
            return None
        return {k: str(v) for k, v in params.items() if v is not None}

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = self._build_url(path)
        clean = self._clean_params(params)
        last_exc: Optional[Exception] = None

        for attempt in range(self._retries + 1):
            try:
                resp = self._client.request(method, url, json=json, params=clean)
                return self._handle_response(resp, attempt)
            except (RateLimitError, httpx.TimeoutException, httpx.ConnectError) as exc:
                last_exc = exc
                if attempt >= self._retries:
                    raise
                delay = self._retry_delay(exc, attempt)
                time.sleep(delay)

        raise last_exc  # type: ignore[misc]

    def _handle_response(self, resp: httpx.Response, attempt: int) -> Any:
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
        if isinstance(exc, RateLimitError):
            return min(exc.retry_after, _MAX_RETRY_DELAY)
        base = min(2**attempt, 10)
        return float(base)
