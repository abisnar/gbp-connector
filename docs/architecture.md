# Architecture

The connector is a small library, but it's structured around three replaceable
abstractions so that auth, transport, and domain code can evolve (and be
tested) independently.

```
┌─────────────────────────────────────────────────────────────────────┐
│                  GoogleBusinessProfileConnector                     │
│                          (facade)                                   │
├────────────────────────────┬────────────────────────────────────────┤
│        accounts            │              locations                 │
│   AccountsResource         │           LocationsResource            │
└──────────┬─────────────────┴──────────────────┬─────────────────────┘
           │                                    │
           ▼                                    ▼
   ┌───────────────────┐                ┌───────────────────┐
   │   AuthProvider    │ ─── injects ─▶ │     HttpClient    │
   │   (Protocol)      │                │     (Protocol)    │
   └───────────────────┘                └───────────────────┘
           ▲                                    ▲
           │                                    │
   ┌───────┴────────┐                  ┌────────┴───────┐
   │ OAuth2Refresh  │                  │   HttpxClient  │
   │ TokenProvider  │                  │                │
   └────────────────┘                  └────────────────┘
```

## SOLID, by file

- **Single Responsibility** — each module owns one concern.
  `auth/` knows tokens. `http/` knows transport. `resources/` knows REST shapes.
  `models/` knows JSON parsing. `connector.py` only wires them together.

- **Open / Closed** — adding a new API surface (e.g. `ReviewsResource`) means
  adding one file under `resources/` and one line in `connector.py`. No
  existing module changes. Same for a new auth strategy
  (service account, ADC): add a class, inject it.

- **Liskov Substitution** — every `AuthProvider` is interchangeable from the
  resources' perspective because the only contract is `get_access_token() -> str`.
  Tests rely on this with `FakeAuth`.

- **Interface Segregation** — `AuthProvider` and `HttpClient` are tiny
  `Protocol`s with one method each. Nothing forces an implementation to carry
  surface area it doesn't use.

- **Dependency Inversion** — `BaseResource` depends on the protocols, not the
  concrete `OAuth2RefreshTokenProvider` / `HttpxClient`. The facade is the only
  place that picks defaults; everything below it sees abstractions.

## Encapsulation

- `ConnectorConfig` is a frozen dataclass — no field can be mutated after
  construction.
- All collaborators (`_auth`, `_http`, `_base_url`) are name-mangled-style
  private; public access is through resource methods or the facade properties.
- The token refresh response is **never** logged or attached to exceptions —
  see `oauth2.py:_refresh` — because Google's error envelope can echo back
  parts of the request.
- Exceptions form a closed hierarchy under `GBPConnectorError`; callers can
  catch one type and still discriminate by subclass when they care.

## Why the OpenAPI spec lives here

`openapi/google-business-profile.yaml` documents the **upstream** contract
this library depends on — the slice of Google's APIs we actually call. It is
not a server we expose. Keeping it in-tree means:

- We can lint it in CI (`redocly lint`), catching breakage if we drift.
- Integration tests / mocks (e.g. `prism mock`, `respx`) have a single source
  of truth.
- Anyone reading the repo can see exactly which endpoints, scopes, and error
  shapes the connector relies on.
