"""Fixtures for integration tests.

Two flavors of connector are built here:

  - ``mock_connector`` — points at a Prism mock server (URL from
    ``GBP_MOCK_BASE_URL``), uses a :class:`StaticTokenProvider` so no real
    OAuth handshake happens. Skips the test cleanly if the env var is missing.

  - ``live_connector`` — built from ``GoogleBusinessProfileConnector.from_env()``
    and only constructed when ``--run-live`` is passed AND all required
    ``GBP_*`` env vars are present. Used by the ``live`` test suite.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

from gbp_connector import (
    ConnectorConfig,
    GoogleBusinessProfileConnector,
    StaticTokenProvider,
)

REQUIRED_LIVE_ENV_VARS = ("GBP_CLIENT_ID", "GBP_CLIENT_SECRET", "GBP_REFRESH_TOKEN")


@pytest.fixture(scope="session")
def mock_base_url() -> str:
    url = os.environ.get("GBP_MOCK_BASE_URL")
    if not url:
        pytest.skip("Set GBP_MOCK_BASE_URL to a running Prism mock to enable.")
    return url


@pytest.fixture()
def mock_connector(mock_base_url: str) -> Iterator[GoogleBusinessProfileConnector]:
    """Connector pointed at the Prism mock; no real auth is performed."""
    config = ConnectorConfig(
        client_id="mock",
        client_secret="mock",
        refresh_token="mock",
        # Both base URLs point at the same Prism instance — Prism routes by
        # path, and our spec's paths are unambiguous across services.
        account_mgmt_base_url=mock_base_url,
        business_info_base_url=mock_base_url,
    )
    connector = GoogleBusinessProfileConnector(
        config=config,
        auth=StaticTokenProvider("mock-bearer-token"),
    )
    try:
        yield connector
    finally:
        connector.close()


@pytest.fixture()
def live_connector() -> Iterator[GoogleBusinessProfileConnector]:
    """Connector wired to real Google APIs from the environment."""
    missing = [name for name in REQUIRED_LIVE_ENV_VARS if not os.environ.get(name)]
    if missing:
        pytest.skip(f"Missing live env vars: {', '.join(missing)}")

    connector = GoogleBusinessProfileConnector.from_env()
    try:
        yield connector
    finally:
        connector.close()


@pytest.fixture()
def live_account_id() -> str:
    """A specific account resource name to probe in live tests.

    Set ``GBP_TEST_ACCOUNT_ID=accounts/1234567890`` to skip the discovery
    round-trip; otherwise tests fall back to listing accounts first.
    """
    account_id = os.environ.get("GBP_TEST_ACCOUNT_ID")
    if not account_id:
        pytest.skip("Set GBP_TEST_ACCOUNT_ID to enable account-scoped live tests.")
    return account_id
