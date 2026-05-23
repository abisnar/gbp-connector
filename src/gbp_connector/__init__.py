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

from gbp_connector.auth import AuthProvider, OAuth2RefreshTokenProvider
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

__version__ = "0.1.0"

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
    "__version__",
]
