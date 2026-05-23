"""Shared resource plumbing: auth headers, error translation, pagination."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

from gbp_connector.auth.base import AuthProvider
from gbp_connector.exceptions import GBPApiError, NotFoundError, RateLimitError
from gbp_connector.http.base import HttpClient, HttpResponse


class BaseResource:
    """Common behavior for every API resource.

    Subclasses are thin: they translate domain operations into HTTP verbs and
    use the helpers here to attach the bearer token, raise typed exceptions,
    and walk paginated responses. Everything else lives in the injected
    collaborators.
    """

    def __init__(self, *, auth: AuthProvider, http: HttpClient, base_url: str) -> None:
        self._auth = auth
        self._http = http
        self._base_url = base_url.rstrip("/")

    # --- protected helpers for subclasses ----------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}/{path.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self._auth.get_access_token()}",
            "Accept": "application/json",
        }
        response = self._http.request(method, url, headers=headers, params=params, json=json)
        if not response.is_success:
            raise _to_exception(response)
        return response.json_body if isinstance(response.json_body, dict) else {}

    def _paginate(
        self,
        method: str,
        path: str,
        *,
        items_key: str,
        params: Mapping[str, Any] | None = None,
        page_size: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Yield items across all pages, transparently following ``nextPageToken``.

        Raises:
            GBPApiError: if the server returns the same ``nextPageToken`` twice
                in a row. That always indicates a broken server (or a mock that
                doesn't advance pages) and would otherwise loop forever.
        """
        page_params: dict[str, Any] = dict(params or {})
        if page_size is not None:
            page_params["pageSize"] = page_size

        previous_token: str | None = None
        while True:
            payload = self._request(method, path, params=page_params)
            yield from payload.get(items_key, []) or []
            next_token = payload.get("nextPageToken")
            if not next_token:
                return
            if next_token == previous_token:
                raise GBPApiError(
                    f"Server returned the same nextPageToken twice "
                    f"({next_token!r}); refusing to loop.",
                    status_code=502,
                )
            previous_token = next_token
            page_params["pageToken"] = next_token


def _to_exception(response: HttpResponse) -> GBPApiError:
    """Map an HTTP failure into the most specific connector exception we have.

    Note: a 401 here means the API rejected the access token, not that the OAuth
    refresh itself failed (that path raises :class:`AuthenticationError` from
    ``oauth2.py``). We keep both signals distinct so callers can tell whether to
    re-prompt for consent or just retry.
    """
    body_snippet = response.text[:500] if response.text else None
    message = _extract_api_message(response.json_body) or "Google Business Profile API error"

    if response.status_code == 404:
        return NotFoundError(message, status_code=404, response_body=body_snippet)
    if response.status_code == 429:
        return RateLimitError(message, status_code=429, response_body=body_snippet)
    return GBPApiError(message, status_code=response.status_code, response_body=body_snippet)


def _extract_api_message(json_body: Any) -> str | None:
    """Pull the human-readable message out of a Google API error envelope."""
    if not isinstance(json_body, dict):
        return None
    error = json_body.get("error")
    if isinstance(error, dict):
        message = error.get("message")
        if isinstance(message, str):
            return message
    return None
