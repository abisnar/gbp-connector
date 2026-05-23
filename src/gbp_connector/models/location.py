"""Location model — a single physical business location on Google Business Profile."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PostalAddress(BaseModel):
    """A subset of google.type.PostalAddress — extend as needs grow."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    region_code: str | None = Field(default=None, alias="regionCode")
    postal_code: str | None = Field(default=None, alias="postalCode")
    administrative_area: str | None = Field(default=None, alias="administrativeArea")
    locality: str | None = None
    address_lines: list[str] | None = Field(default=None, alias="addressLines")


class Location(BaseModel):
    """A Business Profile location.

    Mirrors the upstream Location resource:
    https://developers.google.com/my-business/reference/businessinformation/rest/v1/accounts.locations
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    name: str = Field(description="Resource name, e.g. 'locations/9876543210'.")
    title: str | None = Field(default=None, description="The location's display name.")
    store_code: str | None = Field(default=None, alias="storeCode")
    phone_numbers: dict[str, str] | None = Field(default=None, alias="phoneNumbers")
    website_uri: str | None = Field(default=None, alias="websiteUri")
    storefront_address: PostalAddress | None = Field(default=None, alias="storefrontAddress")
    primary_category: dict[str, str] | None = Field(default=None, alias="primaryCategory")
    labels: list[str] | None = None
