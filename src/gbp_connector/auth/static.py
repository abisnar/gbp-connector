"""Static-token auth provider.

A trivial :class:`AuthProvider` that returns a token the caller already has.
Useful for:

  - tests against a mock server (no OAuth roundtrip)
  - environments where another component (e.g. ADC, a sidecar) hands you a
    fresh access token and you just want the connector to use it
  - short-lived scripts where you've manually run the consent flow once and
    pasted an access token into your shell

Do **not** use this with a long-lived secret as the "token" — the value here
is sent as ``Authorization: Bearer <value>`` on every call, so it must be an
actual OAuth access token.
"""

from __future__ import annotations


class StaticTokenProvider:
    """Returns a pre-supplied access token unchanged on every call."""

    __slots__ = ("_token",)

    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("StaticTokenProvider requires a non-empty token")
        self._token = token

    def get_access_token(self) -> str:
        return self._token
