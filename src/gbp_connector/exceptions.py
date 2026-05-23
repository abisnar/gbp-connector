"""Exception hierarchy for gbp-connector.

All errors raised by this library inherit from :class:`GBPConnectorError`, so
callers can catch that one type to handle every failure mode the connector
produces.
"""

from __future__ import annotations


class GBPConnectorError(Exception):
    """Base class for every exception raised by gbp-connector."""


class ConfigurationError(GBPConnectorError):
    """Raised when the connector is configured incorrectly (missing creds, etc.)."""


class AuthenticationError(GBPConnectorError):
    """Raised when an OAuth token cannot be obtained or refreshed."""


class GBPApiError(GBPConnectorError):
    """Raised when the Google Business Profile API returns a non-2xx response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:  # pragma: no cover — trivial formatting
        base = super().__str__()
        return f"[{self.status_code}] {base}"


class NotFoundError(GBPApiError):
    """Raised on HTTP 404 from the API."""


class RateLimitError(GBPApiError):
    """Raised on HTTP 429 from the API."""
