# Usage

Runnable recipes for the most common things you'll do with `gbp-connector`.
Each snippet assumes the env vars from [oauth-setup.md](oauth-setup.md) are
set and that you've installed the package (`pip install gbp-connector`).

## Construct the connector

```python
from gbp_connector import GoogleBusinessProfileConnector

# Reads GBP_CLIENT_ID, GBP_CLIENT_SECRET, GBP_REFRESH_TOKEN from the environment.
with GoogleBusinessProfileConnector.from_env() as gbp:
    ...  # use gbp.accounts / gbp.locations
```

The context-manager form releases the HTTP connection pool when you're done.
For long-lived processes, hold one connector for the lifetime of the process
and call `.close()` at shutdown.

## List accounts

```python
with GoogleBusinessProfileConnector.from_env() as gbp:
    for account in gbp.accounts.list():
        print(account.name, account.account_name, account.role)
```

`list()` returns an iterator — it transparently follows `nextPageToken` so
you never see pagination tokens.

## Fetch a single account

```python
account = gbp.accounts.get("accounts/1234567890")
```

A missing account raises [`NotFoundError`](../src/gbp_connector/exceptions.py).

## List locations under an account

```python
for location in gbp.locations.list("accounts/1234567890"):
    print(location.name, location.title, location.website_uri)
```

By default the connector requests a sensible subset of fields. To return
more, pass a custom `read_mask`:

```python
gbp.locations.list(
    "accounts/1234567890",
    read_mask="name,title,profile,regularHours,latlng",
)
```

The field names are Google's (camelCase), not the Python ones.

## Update a single field on a location

```python
updated = gbp.locations.patch(
    "locations/9876543210",
    updates={"websiteUri": "https://example.com"},
    update_mask="websiteUri",
)
print("New URL:", updated.website_uri)
```

`update_mask` is **required**. The Business Information API ignores any
field that isn't in the mask — even if it appears in `updates`. The
connector enforces this in the method signature so you can't accidentally
send a PATCH that no-ops.

### Dry-run a PATCH

```python
gbp.locations.patch(
    "locations/9876543210",
    updates={"websiteUri": "https://example.com"},
    update_mask="websiteUri",
    validate_only=True,
)
```

The API validates the request and returns the same shape but never persists.
Use this on first deploy or in CI sanity checks.

## Handle errors

```python
from gbp_connector import GBPApiError, NotFoundError, RateLimitError

try:
    gbp.locations.get("locations/does-not-exist")
except NotFoundError as e:
    print("Gone:", e)                       # status_code == 404
except RateLimitError as e:
    print("Slow down:", e)                  # status_code == 429
except GBPApiError as e:
    print(f"API error {e.status_code}: {e}")
```

Every exception the library raises is a subclass of
[`GBPConnectorError`](../src/gbp_connector/exceptions.py), so a single catch
is enough when you don't need to discriminate.

## Inject your own HTTP client (retries, proxies)

```python
import httpx
from gbp_connector import (
    GoogleBusinessProfileConnector, ConnectorConfig, HttpxClient,
)

http = HttpxClient(
    client=httpx.Client(
        timeout=httpx.Timeout(30.0, connect=5.0),
        transport=httpx.HTTPTransport(retries=3),
        proxy="http://corporate-proxy:8080",
    ),
)
gbp = GoogleBusinessProfileConnector(
    config=ConnectorConfig.from_env(),
    http=http,
)
```

Any object with a `request(method, url, *, headers, params, json, data, timeout)`
method that returns an [`HttpResponse`](../src/gbp_connector/http/base.py)
satisfies the protocol — you can plug in your own retry/circuit-breaker
wrapper without subclassing anything in this library.

## Inject your own auth (service account, ADC, etc.)

```python
from gbp_connector import GoogleBusinessProfileConnector, ConnectorConfig

class ServiceAccountAuth:
    def __init__(self, credentials): ...
    def get_access_token(self) -> str:
        # … refresh from your credentials object …
        return self._token

gbp = GoogleBusinessProfileConnector(
    config=ConnectorConfig.from_env(),  # GBP_REFRESH_TOKEN is unused in this path
    auth=ServiceAccountAuth(my_creds),
)
```

For the "I already have a token" case, use the built-in
[`StaticTokenProvider`](../src/gbp_connector/auth/static.py):

```python
from gbp_connector import StaticTokenProvider

gbp = GoogleBusinessProfileConnector(
    config=ConnectorConfig(client_id="x", client_secret="x", refresh_token="x"),
    auth=StaticTokenProvider("ya29.…"),
)
```
