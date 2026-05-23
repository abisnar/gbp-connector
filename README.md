# gbp-connector

A typed, dependency-injectable Python client for the
[Google Business Profile](https://developers.google.com/my-business) API.

[![CI](https://github.com/abisnar/gbp-connector/actions/workflows/ci.yml/badge.svg)](https://github.com/abisnar/gbp-connector/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

```python
from gbp_connector import GoogleBusinessProfileConnector

with GoogleBusinessProfileConnector.from_env() as gbp:
    for account in gbp.accounts.list():
        print(account.name, account.account_name)

    updated = gbp.locations.patch(
        "locations/9876543210",
        updates={"websiteUri": "https://example.com"},
        update_mask="websiteUri",
    )
    print("Updated:", updated.website_uri)
```

## Why this exists

Google's Business Profile API is REST-with-quirks: separate base URLs per
service, mandatory `readMask`/`updateMask` query params, OAuth-only auth,
quota gates that require a one-time approval. This library hides all of that
behind a small, typed surface and stays out of your way for the parts that
matter (which fields to update, which account to operate on).

## Install

```bash
pip install gbp-connector
# or, with uv
uv add gbp-connector
```

Requires Python 3.11+.

## Configure

The library reads three secrets from the environment:

```bash
export GBP_CLIENT_ID="…apps.googleusercontent.com"
export GBP_CLIENT_SECRET="…"
export GBP_REFRESH_TOKEN="…"
```

Getting those values is a one-time setup — see [docs/oauth-setup.md](docs/oauth-setup.md).

**No secrets in the repo.** `.env` is gitignored, `.env.example` shows the
shape, and CI runs `gitleaks` on every push as a backstop.

## Design

Three replaceable abstractions, wired together by a facade:

- `AuthProvider`  — yields a current access token (`OAuth2RefreshTokenProvider` by default)
- `HttpClient`    — performs HTTP requests (`HttpxClient` by default)
- `BaseResource`  — domain-grouped API methods (`AccountsResource`, `LocationsResource`)

Each is a small `typing.Protocol`. Swap any of them in the constructor to
test, mock, or extend:

```python
from gbp_connector import GoogleBusinessProfileConnector, ConnectorConfig

connector = GoogleBusinessProfileConnector(
    config=ConnectorConfig(client_id="…", client_secret="…", refresh_token="…"),
    auth=MyServiceAccountAuth(...),        # alt AuthProvider
    http=MyRetryingHttpClient(...),        # alt HttpClient
)
```

More:

- [docs/usage.md](docs/usage.md) — runnable recipes (list, get, patch, custom auth/http, error handling)
- [docs/architecture.md](docs/architecture.md) — how SOLID maps onto the layout
- [docs/testing.md](docs/testing.md) — unit / mock / live test tiers and how to run them
- [docs/oauth-setup.md](docs/oauth-setup.md) — one-time OAuth client + refresh-token setup
- [examples/](examples/) — runnable scripts you can copy

## OpenAPI spec

[`openapi/google-business-profile.yaml`](openapi/google-business-profile.yaml)
describes the **subset of Google's API** that this library depends on
(accounts list/get, locations list/get/patch, error shapes, OAuth scope). It's
linted in CI with `redocly` so we notice if we drift.

This library is an SDK, not a server — the spec exists to pin the upstream
contract, not to publish one of our own.

## Development

```bash
uv pip install -e ".[dev]"

ruff check . && ruff format --check .
mypy
pytest
```

The default `pytest` invocation is offline-only against `FakeHttpClient` /
`FakeAuth`; the unit suite finishes in well under a second. Integration and
live tests are opt-in — see [docs/testing.md](docs/testing.md) and
[CONTRIBUTING.md](CONTRIBUTING.md).

## CI

`.github/workflows/ci.yml` runs these jobs on every push and PR:

| Job              | What it does                                                            |
|------------------|-------------------------------------------------------------------------|
| lint-and-type    | `ruff check`, `ruff format --check`, `mypy --strict`                    |
| test             | `pytest` unit suite across Python 3.11 / 3.12 / 3.13                    |
| integration-mock | Boots `prism mock` from the OpenAPI spec, runs integration tests        |
| openapi          | `redocly lint` on `openapi/google-business-profile.yaml`                |
| secret-scan      | `gitleaks` over the full history                                        |

Live tests against real Google APIs are **not** run in CI — they need real
credentials. Run them locally per [docs/testing.md](docs/testing.md).

## License

MIT — see [LICENSE](LICENSE).
