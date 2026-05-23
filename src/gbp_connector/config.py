"""Connector configuration loaded from environment variables.

Keeping configuration as a frozen dataclass makes it explicit and testable —
no module-level reads, no surprise mutation, no secrets in source.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from gbp_connector.exceptions import ConfigurationError

DEFAULT_TOKEN_URI = "https://oauth2.googleapis.com/token"
DEFAULT_ACCOUNT_MGMT_BASE_URL = "https://mybusinessaccountmanagement.googleapis.com/v1"
DEFAULT_BUSINESS_INFO_BASE_URL = "https://mybusinessbusinessinformation.googleapis.com/v1"


@dataclass(frozen=True, slots=True)
class ConnectorConfig:
    """Immutable bundle of configuration for the connector.

    Required:
        client_id, client_secret, refresh_token

    Optional (sensible defaults provided):
        token_uri, account_mgmt_base_url, business_info_base_url, default_account_id
    """

    client_id: str
    client_secret: str
    refresh_token: str
    token_uri: str = DEFAULT_TOKEN_URI
    account_mgmt_base_url: str = DEFAULT_ACCOUNT_MGMT_BASE_URL
    business_info_base_url: str = DEFAULT_BUSINESS_INFO_BASE_URL
    default_account_id: str | None = None

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> ConnectorConfig:
        """Build a :class:`ConnectorConfig` from environment variables.

        Reads ``GBP_CLIENT_ID``, ``GBP_CLIENT_SECRET``, ``GBP_REFRESH_TOKEN`` (required)
        and ``GBP_TOKEN_URI``, ``GBP_ACCOUNT_ID`` (optional).

        Raises:
            ConfigurationError: when any required variable is missing or blank.
        """
        source = env if env is not None else os.environ

        def _required(key: str) -> str:
            value = source.get(key, "").strip()
            if not value:
                raise ConfigurationError(
                    f"Missing required environment variable: {key}. "
                    "Copy .env.example to .env and fill it in, or set it in your "
                    "deployment environment."
                )
            return value

        return cls(
            client_id=_required("GBP_CLIENT_ID"),
            client_secret=_required("GBP_CLIENT_SECRET"),
            refresh_token=_required("GBP_REFRESH_TOKEN"),
            token_uri=source.get("GBP_TOKEN_URI", DEFAULT_TOKEN_URI).strip() or DEFAULT_TOKEN_URI,
            default_account_id=(source.get("GBP_ACCOUNT_ID", "").strip() or None),
        )
