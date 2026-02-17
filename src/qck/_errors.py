"""QCK SDK error classes."""

from __future__ import annotations


class QCKError(Exception):
    """Base error for all QCK API errors."""

    def __init__(self, message: str, status: int, code: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code


class AuthenticationError(QCKError):
    """Raised when API key is invalid or missing."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, 401, "AUTHENTICATION_ERROR")


class RateLimitError(QCKError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60) -> None:
        super().__init__(message, 429, "RATE_LIMIT_ERROR")
        self.retry_after = retry_after


class NotFoundError(QCKError):
    """Raised when the requested resource is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, 404, "NOT_FOUND")


class ValidationError(QCKError):
    """Raised when request validation fails."""

    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message, 400, "VALIDATION_ERROR")
