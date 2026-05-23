"""Top-level facade that wires every collaborator together.

Most callers should construct the connector via :meth:`from_env`; the explicit
constructor exists so tests and advanced users can inject substitute auth,
HTTP, and resource implementations.
"""

from __future__ import annotations

from collections.abc import Mapping

from gbp_connector.auth.base import AuthProvider
from gbp_connector.auth.oauth2 import OAuth2RefreshTokenProvider
from gbp_connector.config import ConnectorConfig
from gbp_connector.http.base import HttpClient
from gbp_connector.http.httpx_client import HttpxClient
from gbp_connector.resources.accounts import AccountsResource
from gbp_connector.resources.locations import LocationsResource


class GoogleBusinessProfileConnector:
    """Entry point for interacting with the Google Business Profile API.

    The connector owns three replaceable collaborators:

    - an :class:`AuthProvider` (default: OAuth2 refresh-token flow)
    - an :class:`HttpClient`   (default: ``httpx``-backed sync client)
    - per-domain resource classes (``accounts``, ``locations``)

    Any of them can be substituted via the constructor for tests or alternate
    deployments — the facade itself contains no business logic, only wiring.
    """

    def __init__(
        self,
        *,
        config: ConnectorConfig,
        auth: AuthProvider | None = None,
        http: HttpClient | None = None,
    ) -> None:
        self._config = config
        self._http: HttpClient = http or HttpxClient()
        self._auth: AuthProvider = auth or OAuth2RefreshTokenProvider(
            client_id=config.client_id,
            client_secret=config.client_secret,
            refresh_token=config.refresh_token,
            http_client=self._http,
            token_uri=config.token_uri,
        )
        self._accounts = AccountsResource(
            auth=self._auth, http=self._http, base_url=config.account_mgmt_base_url
        )
        self._locations = LocationsResource(
            auth=self._auth, http=self._http, base_url=config.business_info_base_url
        )

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> GoogleBusinessProfileConnector:
        """Build a connector from ``GBP_*`` environment variables.

        See :meth:`ConnectorConfig.from_env` for the variable list.
        """
        return cls(config=ConnectorConfig.from_env(env))

    @property
    def accounts(self) -> AccountsResource:
        return self._accounts

    @property
    def locations(self) -> LocationsResource:
        return self._locations

    @property
    def config(self) -> ConnectorConfig:
        return self._config

    def close(self) -> None:
        """Release the underlying HTTP client if it's an :class:`HttpxClient`."""
        close = getattr(self._http, "close", None)
        if callable(close):
            close()

    def __enter__(self) -> GoogleBusinessProfileConnector:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
