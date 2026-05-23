"""Account model — a Google Business Profile account that owns locations."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Account(BaseModel):
    """A Business Profile account.

    Field names follow Google's API (camelCase on the wire, snake_case in
    Python via ``Field(alias=...)``). See:
    https://developers.google.com/my-business/reference/accountmanagement/rest/v1/accounts
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    name: str = Field(description="Resource name, e.g. 'accounts/1234567890'.")
    account_name: str | None = Field(
        default=None,
        alias="accountName",
        description="Human-readable account name.",
    )
    type: str | None = Field(
        default=None,
        description="Account type, e.g. PERSONAL, LOCATION_GROUP, ORGANIZATION.",
    )
    role: str | None = Field(
        default=None,
        description="The caller's role on this account, e.g. OWNER, MANAGER.",
    )
    verification_state: str | None = Field(default=None, alias="verificationState")
