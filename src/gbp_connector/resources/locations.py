"""Locations resource — read and patch business locations."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from gbp_connector.models.location import Location
from gbp_connector.resources.base import BaseResource

# The Business Information API requires the caller to declare which fields to
# return when listing. Keep this list narrow and predictable; callers that need
# more can pass their own ``read_mask``.
_DEFAULT_LOCATION_READ_MASK = (
    "name,title,storeCode,phoneNumbers,websiteUri,storefrontAddress,primaryCategory,labels"
)


class LocationsResource(BaseResource):
    """Operations on locations under a given account.

    Backed by the Business Information API
    (``mybusinessbusinessinformation.googleapis.com/v1``).
    """

    def list(
        self,
        account_id: str,
        *,
        read_mask: str = _DEFAULT_LOCATION_READ_MASK,
        page_size: int | None = None,
        filter_: str | None = None,
    ) -> Iterator[Location]:
        """Iterate over locations under ``account_id`` (e.g. ``accounts/1234567890``)."""
        params: dict[str, Any] = {"readMask": read_mask}
        if filter_:
            params["filter"] = filter_
        for raw in self._paginate(
            "GET",
            f"/{account_id}/locations",
            items_key="locations",
            params=params,
            page_size=page_size,
        ):
            yield Location.model_validate(raw)

    def get(self, location_id: str, *, read_mask: str = _DEFAULT_LOCATION_READ_MASK) -> Location:
        """Fetch a single location (``locations/9876543210``)."""
        payload = self._request("GET", f"/{location_id}", params={"readMask": read_mask})
        return Location.model_validate(payload)

    def patch(
        self,
        location_id: str,
        *,
        updates: dict[str, Any],
        update_mask: str,
        validate_only: bool = False,
    ) -> Location:
        """Update specific fields on a location.

        Google's Business Information API requires every PATCH to declare an
        ``updateMask`` listing exactly which fields will be written; anything
        not in the mask is ignored even if present in the body. We make that
        explicit in the signature so callers can't accidentally send a body
        that does nothing.

        Args:
            location_id: Resource name (``locations/9876543210``).
            updates: Partial Location body — only the fields in ``update_mask``
                will be applied. Use API field names (camelCase).
            update_mask: Comma-separated FieldMask, e.g. ``"websiteUri,phoneNumbers"``.
            validate_only: If True, the API validates the request without writing.
        """
        params: dict[str, Any] = {"updateMask": update_mask}
        if validate_only:
            params["validateOnly"] = "true"
        payload = self._request("PATCH", f"/{location_id}", params=params, json=updates)
        return Location.model_validate(payload)
