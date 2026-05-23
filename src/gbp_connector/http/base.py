"""Transport-agnostic HTTP protocol.

Defining ``HttpClient`` as a :class:`typing.Protocol` (structural typing) means
implementations don't need to inherit from anything — they just need a
``request`` method with the matching signature. This makes mocking trivial:
any object with the right shape works.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class HttpResponse:
    """A minimal, transport-agnostic HTTP response.

    Only the fields the connector actually needs are exposed. Adding more later
    (e.g. ``elapsed``) is non-breaking; consumers depend on what's here today.
    """

    status_code: int
    text: str
    headers: Mapping[str, str] = field(default_factory=dict)
    json_body: Any = None

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300


@runtime_checkable
class HttpClient(Protocol):
    """Performs a single synchronous HTTP request.

    Implementations MUST:
      - Send the request as specified (do not retry transparently — that's the
        caller's policy decision).
      - Parse JSON bodies into ``json_body`` when ``Content-Type`` indicates JSON,
        otherwise leave it as ``None``.
      - Never raise on non-2xx status codes — return the response and let the
        domain layer decide how to react.
      - Raise only on transport failures (connection refused, timeout, etc.).
    """

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
    ) -> HttpResponse: ...
