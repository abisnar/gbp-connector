"""Authentication protocol.

The connector never reaches into an auth implementation's internals — it only
asks for a bearer token. That single-method contract is what lets us swap the
default OAuth2 refresh-token flow for a service account, an Application Default
Credentials provider, or a test stub, with zero changes to the rest of the code.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class AuthProvider(Protocol):
    """Yields a valid OAuth2 access token suitable for ``Authorization: Bearer``.

    Implementations are responsible for caching and refreshing as needed; callers
    should treat the returned string as opaque and short-lived.
    """

    def get_access_token(self) -> str: ...
