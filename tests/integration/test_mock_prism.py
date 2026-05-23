"""Integration tests against a Prism mock of the OpenAPI spec.

These tests verify the **client ↔ spec** contract: that the requests our
resources actually send match the paths, methods, params, and bodies declared
in ``openapi/google-business-profile.yaml``, and that we can parse the
responses Prism generates from the spec.

Run with::

    GBP_MOCK_BASE_URL=http://localhost:4010 pytest tests/integration --run-integration

The Prism server itself is started by CI (see ``.github/workflows/ci.yml``)
or locally via the recipe in ``docs/testing.md``.
"""

from __future__ import annotations

import pytest

from gbp_connector import Account, GoogleBusinessProfileConnector, Location

pytestmark = pytest.mark.integration


def test_list_accounts_returns_typed_models(mock_connector: GoogleBusinessProfileConnector) -> None:
    """Iterating accounts against the mock should yield validated Account models."""
    accounts = list(mock_connector.accounts.list())
    # Prism may return zero or more — both are valid. What we care about is
    # the types and that no exception escaped.
    assert all(isinstance(a, Account) for a in accounts)


def test_get_account_returns_typed_model(mock_connector: GoogleBusinessProfileConnector) -> None:
    account = mock_connector.accounts.get("accounts/1234567890")
    assert isinstance(account, Account)
    assert account.name.startswith("accounts/")


def test_list_locations_returns_typed_models(
    mock_connector: GoogleBusinessProfileConnector,
) -> None:
    locations = list(mock_connector.locations.list("accounts/1234567890"))
    assert all(isinstance(loc, Location) for loc in locations)


def test_get_location_returns_typed_model(
    mock_connector: GoogleBusinessProfileConnector,
) -> None:
    location = mock_connector.locations.get("locations/9876543210")
    assert isinstance(location, Location)
    assert location.name.startswith("locations/")


def test_patch_location_round_trips(
    mock_connector: GoogleBusinessProfileConnector,
) -> None:
    """A PATCH with an updateMask should return a valid Location body."""
    updated = mock_connector.locations.patch(
        "locations/9876543210",
        updates={"websiteUri": "https://contract-test.example"},
        update_mask="websiteUri",
    )
    assert isinstance(updated, Location)
