"""Tests for ConnectorConfig.from_env."""

from __future__ import annotations

import pytest

from gbp_connector.config import (
    DEFAULT_ACCOUNT_MGMT_BASE_URL,
    DEFAULT_BUSINESS_INFO_BASE_URL,
    DEFAULT_TOKEN_URI,
    ConnectorConfig,
)
from gbp_connector.exceptions import ConfigurationError


def test_from_env_uses_required_values() -> None:
    cfg = ConnectorConfig.from_env(
        {
            "GBP_CLIENT_ID": "cid",
            "GBP_CLIENT_SECRET": "secret",
            "GBP_REFRESH_TOKEN": "rtok",
        }
    )
    assert cfg.client_id == "cid"
    assert cfg.client_secret == "secret"
    assert cfg.refresh_token == "rtok"
    assert cfg.token_uri == DEFAULT_TOKEN_URI
    assert cfg.account_mgmt_base_url == DEFAULT_ACCOUNT_MGMT_BASE_URL
    assert cfg.business_info_base_url == DEFAULT_BUSINESS_INFO_BASE_URL
    assert cfg.default_account_id is None


def test_from_env_picks_up_optionals() -> None:
    cfg = ConnectorConfig.from_env(
        {
            "GBP_CLIENT_ID": "cid",
            "GBP_CLIENT_SECRET": "secret",
            "GBP_REFRESH_TOKEN": "rtok",
            "GBP_TOKEN_URI": "https://example/token",
            "GBP_ACCOUNT_ID": "accounts/42",
        }
    )
    assert cfg.token_uri == "https://example/token"
    assert cfg.default_account_id == "accounts/42"


@pytest.mark.parametrize("missing", ["GBP_CLIENT_ID", "GBP_CLIENT_SECRET", "GBP_REFRESH_TOKEN"])
def test_from_env_raises_when_required_missing(missing: str) -> None:
    env = {
        "GBP_CLIENT_ID": "cid",
        "GBP_CLIENT_SECRET": "secret",
        "GBP_REFRESH_TOKEN": "rtok",
    }
    env.pop(missing)
    with pytest.raises(ConfigurationError, match=missing):
        ConnectorConfig.from_env(env)


def test_from_env_treats_blank_as_missing() -> None:
    with pytest.raises(ConfigurationError, match="GBP_CLIENT_ID"):
        ConnectorConfig.from_env(
            {"GBP_CLIENT_ID": "   ", "GBP_CLIENT_SECRET": "s", "GBP_REFRESH_TOKEN": "r"}
        )


def test_config_is_frozen() -> None:
    cfg = ConnectorConfig(client_id="a", client_secret="b", refresh_token="c")
    with pytest.raises((AttributeError, TypeError)):
        cfg.client_id = "x"  # type: ignore[misc]
