# Contributing

Thanks for considering a contribution. This document covers the dev workflow,
the style we ship, and what we look for in a PR.

## Dev setup

```bash
git clone https://github.com/abisnar/gbp-connector.git
cd gbp-connector

# uv handles Python + deps in one go
uv venv --python 3.12
uv pip install -e ".[dev]"
```

Then in your shell:

```bash
source .venv/bin/activate
```

## The four checks CI runs

Run them locally before pushing:

```bash
ruff check .              # lint
ruff format --check .     # formatting
mypy                      # strict type-check
pytest                    # unit suite (no network)
```

Everything is configured in `pyproject.toml`; there are no per-tool config
files to keep in sync.

For the OpenAPI spec:

```bash
npm install -g @redocly/cli
redocly lint openapi/google-business-profile.yaml
```

## Coding style

- **One concern per module.** If a file is doing two things, split it.
- **Inject collaborators**, don't reach for module-level singletons. The
  whole point of the `AuthProvider` / `HttpClient` protocols is that the
  resource classes never know who supplied them.
- **Frozen configs.** Mutable shared state is a bug; `dataclass(frozen=True,
  slots=True)` is the norm.
- **Encapsulate secrets.** Never log, never attach to exceptions, never
  return from a public method. `auth/oauth2.py:_refresh` is the canonical
  example.
- **`from __future__ import annotations` at the top of every module.**
  Keeps annotations as strings, lets us use 3.12+ syntax without runtime
  cost.

## Adding a new API resource

1. Add a Pydantic model in `src/gbp_connector/models/`.
2. Add the resource class in `src/gbp_connector/resources/`, subclassing
   `BaseResource`. Use `self._request` and `self._paginate` — don't build
   URLs or attach headers by hand.
3. Wire it into the facade in `src/gbp_connector/connector.py` as a
   `@property`.
4. Export it from `src/gbp_connector/__init__.py`.
5. Add the endpoints to `openapi/google-business-profile.yaml`.
6. Tests:
   - Unit test against `FakeHttpClient` (assert URL, params, body, parsed model).
   - One Prism integration test that exercises the happy path against the spec.
7. Update the `CHANGELOG.md` under `[Unreleased]`.

## PR checklist

- [ ] All four CI checks pass locally
- [ ] OpenAPI spec updated if you added/changed an endpoint
- [ ] A test covers the new behavior
- [ ] `CHANGELOG.md` updated
- [ ] No new secrets, credentials, or `.env`-shaped files in the diff
- [ ] Doc updated if the public API changed (`docs/usage.md`, `README.md`)

## What we will not merge

- Logging or printing the OAuth client secret, refresh token, or access token.
- Mutable global state in the library code path.
- A new resource without a Prism integration test.
- "Just to make CI green" suppressions of mypy or ruff without a comment
  explaining why.
- A live integration test that writes to a real Business Profile without
  `validate_only=True`.
