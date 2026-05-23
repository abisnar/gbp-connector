"""Default :class:`HttpClient` implementation backed by ``httpx``."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from gbp_connector.http.base import HttpResponse

DEFAULT_TIMEOUT_SECONDS = 30.0


class HttpxClient:
    """``HttpClient`` implementation that delegates to a long-lived ``httpx.Client``.

    Reusing one client preserves the underlying HTTP/1.1 connection pool, which
    matters when the connector makes many calls back-to-back (e.g. paginating
    locations across a large account).
    """

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        user_agent: str = "gbp-connector/0.1",
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout)
        self._user_agent = user_agent

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Mapping[str, Any] | None = None,
        timeout: float | None = None,
    ) -> HttpResponse:
        merged_headers: dict[str, str] = {"User-Agent": self._user_agent}
        if headers:
            merged_headers.update(headers)

        response = self._client.request(
            method=method,
            url=url,
            headers=merged_headers,
            params=dict(params) if params else None,
            json=json,
            data=dict(data) if data else None,
            timeout=timeout if timeout is not None else httpx.USE_CLIENT_DEFAULT,
        )
        json_body: Any = None
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type and response.content:
            try:
                json_body = response.json()
            except ValueError:
                json_body = None

        return HttpResponse(
            status_code=response.status_code,
            text=response.text,
            headers=dict(response.headers),
            json_body=json_body,
        )

    def close(self) -> None:
        """Close the underlying ``httpx.Client`` if we created it."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> HttpxClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
