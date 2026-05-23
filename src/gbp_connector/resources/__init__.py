"""Domain-grouped wrappers around the Business Profile API.

Each resource class hides URL construction, auth, pagination, and error
translation behind ordinary Python methods. Adding a new resource means
subclassing :class:`BaseResource` — no other module changes.
"""

from gbp_connector.resources.accounts import AccountsResource
from gbp_connector.resources.base import BaseResource
from gbp_connector.resources.locations import LocationsResource

__all__ = ["AccountsResource", "BaseResource", "LocationsResource"]
