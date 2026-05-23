"""Tests for AccountsResource and LocationsResource."""

from __future__ import annotations

import pytest

from gbp_connector.exceptions import GBPApiError, NotFoundError, RateLimitError
from gbp_connector.http.base import HttpResponse
from gbp_connector.resources.accounts import AccountsResource
from gbp_connector.resources.locations import LocationsResource
from tests.conftest import FakeAuth, FakeHttpClient, json_response

# --- AccountsResource --------------------------------------------------------


def test_accounts_list_iterates_pages(fake_auth: FakeAuth) -> None:
    pages = iter(
        [
            json_response(
                {
                    "accounts": [
                        {"name": "accounts/1", "accountName": "Alpha"},
                        {"name": "accounts/2", "accountName": "Beta"},
                    ],
                    "nextPageToken": "tok-2",
                }
            ),
            json_response({"accounts": [{"name": "accounts/3", "accountName": "Gamma"}]}),
        ]
    )
    http = FakeHttpClient(lambda _call: next(pages))
    resource = AccountsResource(auth=fake_auth, http=http, base_url="https://api.example/v1")

    names = [a.name for a in resource.list()]

    assert names == ["accounts/1", "accounts/2", "accounts/3"]
    assert len(http.calls) == 2
    assert http.calls[1].params == {"pageToken": "tok-2"}


def test_paginate_raises_when_token_repeats(fake_auth: FakeAuth) -> None:
    """A server stuck on the same nextPageToken would otherwise loop forever."""
    stuck = json_response({"accounts": [{"name": "accounts/1"}], "nextPageToken": "stuck"})
    http = FakeHttpClient(stuck)
    resource = AccountsResource(auth=fake_auth, http=http, base_url="https://api.example/v1")

    with pytest.raises(GBPApiError, match="same nextPageToken twice"):
        list(resource.list())


def test_accounts_list_sends_bearer_token(fake_auth: FakeAuth) -> None:
    http = FakeHttpClient(json_response({"accounts": []}))
    resource = AccountsResource(auth=fake_auth, http=http, base_url="https://api.example/v1")

    list(resource.list())

    assert http.calls[0].headers["Authorization"] == "Bearer test-access-token"
    assert fake_auth.call_count == 1


def test_accounts_get_validates_response(fake_auth: FakeAuth) -> None:
    http = FakeHttpClient(
        json_response({"name": "accounts/1", "accountName": "Alpha", "role": "OWNER"})
    )
    resource = AccountsResource(auth=fake_auth, http=http, base_url="https://api.example/v1")

    account = resource.get("accounts/1")

    assert account.account_name == "Alpha"
    assert account.role == "OWNER"
    assert http.calls[0].url == "https://api.example/v1/accounts/1"


# --- LocationsResource -------------------------------------------------------


def test_locations_list_sends_read_mask(fake_auth: FakeAuth) -> None:
    http = FakeHttpClient(json_response({"locations": []}))
    resource = LocationsResource(auth=fake_auth, http=http, base_url="https://api.example/v1")

    list(resource.list("accounts/42"))

    assert http.calls[0].url == "https://api.example/v1/accounts/42/locations"
    assert "readMask" in http.calls[0].params


def test_locations_patch_requires_update_mask(fake_auth: FakeAuth) -> None:
    http = FakeHttpClient(
        json_response({"name": "locations/9", "websiteUri": "https://new.example"})
    )
    resource = LocationsResource(auth=fake_auth, http=http, base_url="https://api.example/v1")

    updated = resource.patch(
        "locations/9",
        updates={"websiteUri": "https://new.example"},
        update_mask="websiteUri",
    )

    call = http.calls[0]
    assert call.method == "PATCH"
    assert call.params == {"updateMask": "websiteUri"}
    assert call.json == {"websiteUri": "https://new.example"}
    assert updated.website_uri == "https://new.example"


def test_locations_patch_validate_only_sets_query_param(fake_auth: FakeAuth) -> None:
    http = FakeHttpClient(json_response({"name": "locations/9"}))
    resource = LocationsResource(auth=fake_auth, http=http, base_url="https://api.example/v1")

    resource.patch("locations/9", updates={"title": "X"}, update_mask="title", validate_only=True)

    assert http.calls[0].params == {"updateMask": "title", "validateOnly": "true"}


# --- error translation -------------------------------------------------------


@pytest.mark.parametrize(
    "status_code,expected",
    [
        (404, NotFoundError),
        (429, RateLimitError),
        (500, GBPApiError),
        (401, GBPApiError),
    ],
)
def test_api_errors_map_to_typed_exceptions(
    fake_auth: FakeAuth, status_code: int, expected: type[Exception]
) -> None:
    http = FakeHttpClient(
        HttpResponse(
            status_code=status_code,
            text='{"error":{"message":"boom"}}',
            headers={"content-type": "application/json"},
            json_body={"error": {"message": "boom"}},
        )
    )
    resource = AccountsResource(auth=fake_auth, http=http, base_url="https://api.example/v1")

    with pytest.raises(expected, match="boom"):
        resource.get("accounts/1")
