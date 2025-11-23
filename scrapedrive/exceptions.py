"""Custom exceptions for ScrapeDrive SDK."""


class ScrapeDriveError(Exception):
    """Base exception for all ScrapeDrive errors."""

    pass


class AuthenticationError(ScrapeDriveError):
    """Raised when authentication fails."""

    pass


class RateLimitError(ScrapeDriveError):
    """Raised when rate limit is exceeded."""

    pass


class ScrapingError(ScrapeDriveError):
    """Raised when scraping fails."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}


class TimeoutError(ScrapeDriveError):
    """Raised when a request times out."""

    pass
