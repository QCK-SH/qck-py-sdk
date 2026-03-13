"""QCK SDK error classes.

Defines the exception hierarchy used throughout the SDK. Every error
raised by the SDK is a subclass of :class:`QCKError`, which itself
extends the built-in :class:`Exception`.

Hierarchy::

    Exception
     +-- QCKError
          +-- AuthenticationError  (HTTP 401)
          +-- RateLimitError       (HTTP 429)
          +-- NotFoundError        (HTTP 404)
          +-- ValidationError      (HTTP 400)
"""

from __future__ import annotations


class QCKError(Exception):
    """Base error for all QCK API errors.

    All exceptions raised by the SDK inherit from this class, so you
    can catch ``QCKError`` to handle any API failure generically.

    Attributes:
        status: HTTP status code returned by the API (e.g. 400, 401).
        code: Machine-readable error code from the API response
            (e.g. ``"VALIDATION_ERROR"``).

    Example:
        >>> try:
        ...     client.links.get("nonexistent")
        ... except QCKError as exc:
        ...     print(exc.status, exc.code)
    """

    def __init__(self, message: str, status: int, code: str) -> None:
        """Initialise the error.

        Args:
            message: Human-readable error description.
            status: HTTP status code.
            code: Machine-readable error code string.
        """
        super().__init__(message)
        self.status = status
        self.code = code


class AuthenticationError(QCKError):
    """Raised when the API key is invalid, expired, or missing.

    This corresponds to an HTTP 401 response. Verify that your API key
    is correct and has not been revoked.

    Attributes:
        status: Always ``401``.
        code: Always ``"AUTHENTICATION_ERROR"``.
    """

    def __init__(self, message: str = "Authentication failed") -> None:
        """Initialise the authentication error.

        Args:
            message: Human-readable error description.
        """
        super().__init__(message, 401, "AUTHENTICATION_ERROR")


class RateLimitError(QCKError):
    """Raised when the API rate limit is exceeded.

    The SDK automatically retries rate-limited requests (up to the
    configured retry count). This exception is raised only after all
    retries have been exhausted.

    Attributes:
        status: Always ``429``.
        code: Always ``"RATE_LIMIT_ERROR"``.
        retry_after: Seconds the server requests you wait before
            retrying (from the ``Retry-After`` response header).
    """

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60) -> None:
        """Initialise the rate-limit error.

        Args:
            message: Human-readable error description.
            retry_after: Seconds to wait before retrying. Defaults to 60.
        """
        super().__init__(message, 429, "RATE_LIMIT_ERROR")
        self.retry_after = retry_after


class NotFoundError(QCKError):
    """Raised when the requested resource does not exist.

    This corresponds to an HTTP 404 response. The link, webhook,
    domain, or other resource referenced by the given ID could not
    be found.

    Attributes:
        status: Always ``404``.
        code: Always ``"NOT_FOUND"``.
    """

    def __init__(self, message: str = "Resource not found") -> None:
        """Initialise the not-found error.

        Args:
            message: Human-readable error description.
        """
        super().__init__(message, 404, "NOT_FOUND")


class ValidationError(QCKError):
    """Raised when request validation fails.

    This corresponds to an HTTP 400 response. Check the error message
    for details about which fields failed validation.

    Attributes:
        status: Always ``400``.
        code: Always ``"VALIDATION_ERROR"``.
    """

    def __init__(self, message: str = "Validation error") -> None:
        """Initialise the validation error.

        Args:
            message: Human-readable error description.
        """
        super().__init__(message, 400, "VALIDATION_ERROR")
