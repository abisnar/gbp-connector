"""Tests for OAuth2RefreshTokenProvider — refresh, caching, error handling."""

from __future__ import annotations

import pytest

from gbp_connector.auth.oauth2 import OAuth2RefreshTokenProvider
from gbp_connector.exceptions import AuthenticationError
from tests.conftest import FakeHttpClient, json_response


def _make_provider(http: FakeHttpClient, *, now: float = 1_000_000.0) -> OAuth2RefreshTokenProvider:
    def clock() -> float:
        return now

    return OAuth2RefreshTokenProvider(
        client_id="cid",
        client_secret="csecret",
        refresh_token="rtok",
        http_client=http,
        token_uri="https://oauth2.example/token",
        clock=clock,
    )


def test_refresh_returns_access_token_and_sends_grant() -> None:
    http = FakeHttpClient(json_response({"access_token": "tok-1", "expires_in": 3600}))
    provider = _make_provider(http)

    assert provider.get_access_token() == "tok-1"

    assert len(http.calls) == 1
    call = http.calls[0]
    assert call.method == "POST"
    assert call.url == "https://oauth2.example/token"
    assert call.data == {
        "client_id": "cid",
        "client_secret": "csecret",
        "refresh_token": "rtok",
        "grant_type": "refresh_token",
    }


def test_token_is_cached_until_near_expiry() -> None:
    responses = iter(
        [
            json_response({"access_token": "tok-1", "expires_in": 3600}),
            json_response({"access_token": "tok-2", "expires_in": 3600}),
        ]
    )
    http = FakeHttpClient(lambda _call: next(responses))
    provider = _make_provider(http)

    assert provider.get_access_token() == "tok-1"
    assert provider.get_access_token() == "tok-1"  # cache hit, no new call
    assert len(http.calls) == 1


def test_token_refreshes_when_within_leeway_of_expiry() -> None:
    responses = iter(
        [
            json_response({"access_token": "tok-1", "expires_in": 30}),  # short-lived
            json_response({"access_token": "tok-2", "expires_in": 3600}),
        ]
    )
    http = FakeHttpClient(lambda _call: next(responses))
    provider = _make_provider(http)

    assert provider.get_access_token() == "tok-1"
    # second call: even though tok-1 hasn't strictly expired, it's inside the
    # 60s leeway, so we refresh
    assert provider.get_access_token() == "tok-2"
    assert len(http.calls) == 2


def test_failure_raises_authentication_error_without_leaking_body() -> None:
    body = "client_secret=csecret&error=invalid_grant"
    from gbp_connector.http.base import HttpResponse

    http = FakeHttpClient(
        HttpResponse(status_code=400, text=body, headers={"content-type": "text/plain"})
    )
    provider = _make_provider(http)

    with pytest.raises(AuthenticationError) as exc:
        provider.get_access_token()
    # The whole point: the secret must not appear in the exception message.
    assert "csecret" not in str(exc.value)
    assert "400" in str(exc.value)


def test_malformed_response_raises_authentication_error() -> None:
    http = FakeHttpClient(json_response({"access_token": "tok-only"}))  # missing expires_in
    provider = _make_provider(http)
    with pytest.raises(AuthenticationError, match="access_token or expires_in"):
        provider.get_access_token()
