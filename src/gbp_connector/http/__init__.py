"""HTTP transport abstractions.

The :class:`HttpClient` protocol is the seam between the connector's domain
code and any real HTTP library. Everything that goes over the wire goes through
this interface, which keeps tests fast (no network) and makes the transport
swappable.
"""

from gbp_connector.http.base import HttpClient, HttpResponse
from gbp_connector.http.httpx_client import HttpxClient

__all__ = ["HttpClient", "HttpResponse", "HttpxClient"]
