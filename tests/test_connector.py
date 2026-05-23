"""Tests for the GoogleBusinessProfileConnector facade."""

from __future__ import annotations

import pytest

from gbp_connector import GoogleBusinessProfileConnector
from gbp_connector.config import ConnectorConfig
from gbp_connector.exceptions import ConfigurationError
from tests.conftest import FakeAuth, FakeHttpClient, json_response


def test_facade_routes_to_accounts_resource(config: ConnectorConfig, fake_auth: FakeAuth) -> None:
    http = FakeHttpClient(json_response({"accounts": []}))
    connector = GoogleBusinessProfileConnector(config=config, auth=fake_auth, http=http)

    list(connector.accounts.list())

    assert http.calls[0].url.startswith(config.account_mgmt_base_url)


def test_facade_routes_to_locations_resource(config: ConnectorConfig, fake_auth: FakeAuth) -> None:
    http = FakeHttpClient(json_response({"locations": []}))
    connector = GoogleBusinessProfileConnector(config=config, auth=fake_auth, http=http)

    list(connector.locations.list("accounts/1"))

    assert http.calls[0].url.startswith(config.business_info_base_url)


def test_from_env_raises_when_unset() -> None:
    with pytest.raises(ConfigurationError):
        GoogleBusinessProfileConnector.from_env({})


def test_from_env_constructs_connector_with_defaults() -> None:
    connector = GoogleBusinessProfileConnector.from_env(
        {
            "GBP_CLIENT_ID": "cid",
            "GBP_CLIENT_SECRET": "secret",
            "GBP_REFRESH_TOKEN": "rtok",
        }
    )
    try:
        assert connector.config.client_id == "cid"
        assert connector.accounts is not None
        assert connector.locations is not None
    finally:
        connector.close()


def test_context_manager_closes_http(config: ConnectorConfig, fake_auth: FakeAuth) -> None:
    closed = {"value": False}

    class ClosableFake(FakeHttpClient):
        def close(self) -> None:
            closed["value"] = True

    http = ClosableFake(json_response({"accounts": []}))
    with GoogleBusinessProfileConnector(config=config, auth=fake_auth, http=http):
        pass
    assert closed["value"] is True
