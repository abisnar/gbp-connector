"""Shared test fixtures and CLI gates.

Unit tests depend only on the public protocols (``AuthProvider``,
``HttpClient``), never on the concrete httpx/OAuth implementations, so the
unit suite runs offline and finishes in well under a second.

Integration tests (``tests/integration/``) are gated behind explicit pytest
flags so they never run by accident:

  - ``--run-integration`` enables tests marked ``integration`` (e.g. those
    that hit a Prism mock server).
  - ``--run-live``        enables tests marked ``live`` (real Google APIs,
    real OAuth credentials from env).

The default ``pytest`` invocation runs the unit suite only.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

import pytest

from gbp_connector.config import ConnectorConfig
from gbp_connector.http.base import HttpResponse

# --- CLI gates for integration / live tests ---------------------------------


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run tests marked 'integration' (e.g. Prism mock server).",
    )
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="Run tests marked 'live' (real Google APIs; needs GBP_* env vars).",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    # Use ``get_closest_marker`` rather than ``"x" in item.keywords`` — the
    # latter also matches directory and filename components (e.g. anything
    # under ``tests/integration/`` would always match "integration").
    run_integration = config.getoption("--run-integration")
    run_live = config.getoption("--run-live")

    skip_integration = pytest.mark.skip(reason="needs --run-integration to run")
    skip_live = pytest.mark.skip(reason="needs --run-live (and GBP_* env vars) to run")

    for item in items:
        if item.get_closest_marker("integration") is not None and not run_integration:
            item.add_marker(skip_integration)
        if item.get_closest_marker("live") is not None and not run_live:
            item.add_marker(skip_live)


# --- Unit-test doubles ------------------------------------------------------


@dataclass
class RecordedRequest:
    """Snapshot of one request the FakeHttpClient received.

    Optional kwargs (headers, params, data) are normalized to empty dicts so
    tests can index them without narrowing.
    """

    method: str
    url: str
    headers: Mapping[str, str] = field(default_factory=dict)
    params: Mapping[str, Any] = field(default_factory=dict)
    json: Any = None
    data: Mapping[str, Any] = field(default_factory=dict)


class FakeHttpClient:
    """In-memory HttpClient that returns canned responses and records calls.

    Pass a single response or a callable ``(request) -> HttpResponse`` for
    multi-step interactions (refresh-then-API, paginated results, etc.).
    """

    def __init__(
        self,
        responder: HttpResponse | Callable[[RecordedRequest], HttpResponse],
    ) -> None:
        self._responder = responder
        self.calls: list[RecordedRequest] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Mapping[str, Any] | None = None,
        timeout: float | None = None,
    ) -> HttpResponse:
        call = RecordedRequest(
            method=method,
            url=url,
            headers=headers or {},
            params=params or {},
            json=json,
            data=data or {},
        )
        self.calls.append(call)
        if callable(self._responder):
            return self._responder(call)
        return self._responder


@dataclass
class FakeAuth:
    """Trivial AuthProvider that hands back a fixed token (and counts calls)."""

    token: str = "test-access-token"
    call_count: int = field(default=0, init=False)

    def get_access_token(self) -> str:
        self.call_count += 1
        return self.token


@pytest.fixture()
def fake_auth() -> FakeAuth:
    return FakeAuth()


@pytest.fixture()
def config() -> ConnectorConfig:
    """A valid config built from explicit (non-env) values."""
    return ConnectorConfig(
        client_id="cid",
        client_secret="csecret",
        refresh_token="rtoken",
        token_uri="https://oauth2.example/token",
        account_mgmt_base_url="https://accountmgmt.example/v1",
        business_info_base_url="https://bizinfo.example/v1",
    )


def json_response(payload: Any, status_code: int = 200) -> HttpResponse:
    """Build a minimal JSON HttpResponse for tests."""
    return HttpResponse(
        status_code=status_code,
        text="",
        headers={"content-type": "application/json"},
        json_body=payload,
    )
