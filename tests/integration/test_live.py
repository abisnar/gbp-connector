"""Live integration tests against the real Google Business Profile API.

These are **read-only by default** and only run when:

  - ``--run-live`` is passed to pytest, AND
  - ``GBP_CLIENT_ID``, ``GBP_CLIENT_SECRET``, ``GBP_REFRESH_TOKEN`` are set.

Mutating tests (PATCH) require an additional explicit env var so they cannot
fire from a misconfigured CI:

  - ``GBP_LIVE_PATCH_LOCATION=locations/...``  — opts the patch test in.
  - ``GBP_LIVE_PATCH_VALUE=https://...``       — the website URI to write.

Even with all of the above the patch test uses ``validate_only=True`` so
nothing on the live profile actually changes — it only checks that the API
accepts the request.
"""

from __future__ import annotations

import os

import pytest

from gbp_connector import Account, GoogleBusinessProfileConnector, Location

pytestmark = pytest.mark.live


def test_live_list_accounts_returns_real_data(
    live_connector: GoogleBusinessProfileConnector,
) -> None:
    """The caller should have at least one account they manage."""
    accounts = list(live_connector.accounts.list(page_size=10))
    assert len(accounts) >= 1, "Expected at least one Business Profile account"
    assert all(isinstance(a, Account) for a in accounts)
    assert all(a.name.startswith("accounts/") for a in accounts)


def test_live_list_locations_for_account(
    live_connector: GoogleBusinessProfileConnector,
    live_account_id: str,
) -> None:
    locations = list(live_connector.locations.list(live_account_id, page_size=10))
    # Zero locations is valid (e.g. a new account); we only verify the types
    # and that the request succeeded.
    assert all(isinstance(loc, Location) for loc in locations)


def test_live_get_specific_location(
    live_connector: GoogleBusinessProfileConnector,
    live_account_id: str,
) -> None:
    locations = list(live_connector.locations.list(live_account_id, page_size=1))
    if not locations:
        pytest.skip(f"{live_account_id} has no locations — nothing to get")
    location = live_connector.locations.get(locations[0].name)
    assert location.name == locations[0].name


def test_live_patch_is_dry_run_safe() -> None:
    """Validate-only PATCH against a real location, no write performed."""
    location_id = os.environ.get("GBP_LIVE_PATCH_LOCATION")
    new_value = os.environ.get("GBP_LIVE_PATCH_VALUE")
    if not location_id or not new_value:
        pytest.skip(
            "Set GBP_LIVE_PATCH_LOCATION and GBP_LIVE_PATCH_VALUE to enable "
            "the validate-only patch test."
        )

    # Build the connector inside the test so the env-gate skip happens cleanly.
    with GoogleBusinessProfileConnector.from_env() as connector:
        result = connector.locations.patch(
            location_id,
            updates={"websiteUri": new_value},
            update_mask="websiteUri",
            validate_only=True,
        )
    assert isinstance(result, Location)
