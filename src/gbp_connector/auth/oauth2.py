"""OAuth2 access token provider using the refresh-token grant.

Google issues a long-lived refresh token after the user completes the OAuth
consent flow once. This provider trades that refresh token for short-lived
access tokens on demand, caches them until just before expiry, and refreshes
when needed.

We deliberately do NOT perform the user-consent flow here — that's a one-time
operation best handled by a small CLI script (see ``docs/oauth-setup.md``).
The library only deals with the long-lived secret + refresh, which is what a
deployed service actually needs.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

from gbp_connector.exceptions import AuthenticationError
from gbp_connector.http.base import HttpClient

# Refresh slightly before expiry so a token never expires mid-request.
_EXPIRY_LEEWAY_SECONDS = 60


class OAuth2RefreshTokenProvider:
    """Caches and refreshes a Google OAuth2 access token.

    Thread-safe: token refresh is serialized with a lock so concurrent callers
    don't all hit the token endpoint at once on cold start.

    Args:
        client_id: OAuth client ID from Google Cloud Console.
        client_secret: OAuth client secret (never log this).
        refresh_token: Long-lived refresh token from the initial consent flow.
        http_client: Transport for calls to the token endpoint. Injected so the
            same HTTP stack/proxy/retry config applies as the rest of the
            connector — and so tests can pass a stub.
        token_uri: Google's OAuth2 token endpoint. Override only for testing.
        clock: Time source (seconds since epoch). Injected for deterministic tests.
    """

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        http_client: HttpClient,
        token_uri: str = "https://oauth2.googleapis.com/token",
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._http = http_client
        self._token_uri = token_uri
        self._clock = clock

        self._lock = threading.Lock()
        self._access_token: str | None = None
        self._expires_at: float = 0.0

    def get_access_token(self) -> str:
        """Return a current access token, refreshing if needed."""
        if self._is_token_fresh():
            assert self._access_token is not None  # narrowed by _is_token_fresh
            return self._access_token

        with self._lock:
            # Double-checked: another thread may have refreshed while we waited.
            if self._is_token_fresh():
                assert self._access_token is not None
                return self._access_token
            self._refresh()
            assert self._access_token is not None
            return self._access_token

    # --- private ----------------------------------------------------------------

    def _is_token_fresh(self) -> bool:
        return (
            self._access_token is not None
            and self._clock() + _EXPIRY_LEEWAY_SECONDS < self._expires_at
        )

    def _refresh(self) -> None:
        response = self._http.request(
            "POST",
            self._token_uri,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
                "grant_type": "refresh_token",
            },
        )

        if not response.is_success or not isinstance(response.json_body, dict):
            # Surface the status code but never the response body — it may echo
            # parts of the request including hints that leak the client_secret.
            raise AuthenticationError(f"Token refresh failed with status {response.status_code}")

        access_token = response.json_body.get("access_token")
        expires_in = response.json_body.get("expires_in")
        if not isinstance(access_token, str) or not isinstance(expires_in, int):
            raise AuthenticationError("Token endpoint response missing access_token or expires_in")

        self._access_token = access_token
        self._expires_at = self._clock() + float(expires_in)
