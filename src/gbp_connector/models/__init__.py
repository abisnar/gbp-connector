"""Pydantic models for Google Business Profile API resources.

Models are intentionally narrow — they describe the fields the connector
exposes today, with ``extra="allow"`` so the upstream API can add fields
without breaking us. When you need a new field, promote it from ``extra``
into an explicit attribute on the model.
"""

from gbp_connector.models.account import Account
from gbp_connector.models.location import Location

__all__ = ["Account", "Location"]
