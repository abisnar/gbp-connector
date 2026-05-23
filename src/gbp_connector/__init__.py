"""gbp-connector — a typed, SOLID Python client for the Google Business Profile API.

Public API:

    from gbp_connector import GoogleBusinessProfileConnector

    connector = GoogleBusinessProfileConnector.from_env()
    for account in connector.accounts.list():
        print(account.name, account.account_name)

The package is organized around three replaceable abstractions:

    - ``AuthProvider``  — supplies a current OAuth2 access token
    - ``HttpClient``    — performs HTTP requests (sync, thin wrapper)
    - ``BaseResource``  — domain-specific API surfaces (accounts, locations, ...)

Swap any of them via constructor injection to test, mock, or extend.
"""

from gbp_connector.auth import AuthProvider, OAuth2RefreshTokenProvider, StaticTokenProvider
from gbp_connector.config import ConnectorConfig
from gbp_connector.connector import GoogleBusinessProfileConnector
from gbp_connector.exceptions import (
    AuthenticationError,
    ConfigurationError,
    GBPApiError,
    GBPConnectorError,
    NotFoundError,
    RateLimitError,
)
from gbp_connector.http import HttpClient, HttpResponse, HttpxClient
from gbp_connector.models import Account, Location
from gbp_connector.resources import AccountsResource, LocationsResource

try:
    # _version.py is generated at build time by hatch-vcs (see pyproject.toml).
    # When running from a non-built checkout it may not exist yet; fall back to
    # a sentinel so imports never break.
    from gbp_connector._version import __version__
except ImportError:  # pragma: no cover — only hit on a raw source checkout
    __version__ = "0.0.0+unknown"

__all__ = [
    "Account",
    "AccountsResource",
    "AuthProvider",
    "AuthenticationError",
    "ConfigurationError",
    "ConnectorConfig",
    "GBPApiError",
    "GBPConnectorError",
    "GoogleBusinessProfileConnector",
    "HttpClient",
    "HttpResponse",
    "HttpxClient",
    "Location",
    "LocationsResource",
    "NotFoundError",
    "OAuth2RefreshTokenProvider",
    "RateLimitError",
    "StaticTokenProvider",
    "__version__",
]
