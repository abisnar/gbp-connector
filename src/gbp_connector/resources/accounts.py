"""Accounts resource — list/get accounts the authenticated user can manage."""

from __future__ import annotations

from collections.abc import Iterator

from gbp_connector.models.account import Account
from gbp_connector.resources.base import BaseResource


class AccountsResource(BaseResource):
    """Operations on Business Profile accounts.

    Backed by the Account Management API
    (``mybusinessaccountmanagement.googleapis.com/v1``).
    """

    def list(self, *, page_size: int | None = None) -> Iterator[Account]:
        """Iterate over all accounts the caller can access.

        Pagination is handled transparently — the caller sees a flat stream.
        """
        for raw in self._paginate("GET", "/accounts", items_key="accounts", page_size=page_size):
            yield Account.model_validate(raw)

    def get(self, account_id: str) -> Account:
        """Fetch a single account by resource name (e.g. ``accounts/1234567890``)."""
        payload = self._request("GET", f"/{account_id}")
        return Account.model_validate(payload)
