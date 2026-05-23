# Testing

The test suite is split into three tiers so you only pay the cost of the
slower tests when you ask for them.

| Tier         | Lives in                | Network? | Default `pytest`? | Trigger                          |
|--------------|-------------------------|----------|-------------------|----------------------------------|
| Unit         | `tests/`                | No       | Yes               | `pytest`                         |
| Integration  | `tests/integration/`    | Local    | No                | `pytest --run-integration` + Prism |
| Live         | `tests/integration/`    | Internet | No                | `pytest --run-live` + GBP_* env  |

## Unit tests

```bash
pytest
```

Drives every code path against `FakeHttpClient` and `FakeAuth` (see
[tests/conftest.py](../tests/conftest.py)). Completes in under a second, no
network or credentials required. This is what CI runs on every push.

## Integration tests against the Prism mock

These verify the **client ↔ spec contract**: the connector's requests match
the paths/methods/params in `openapi/google-business-profile.yaml`, and the
client can parse the responses Prism generates from the spec.

```bash
# In one terminal:
npm install -g @stoplight/prism-cli
prism mock openapi/google-business-profile.yaml --port 4010

# In another:
GBP_MOCK_BASE_URL=http://localhost:4010 \
  pytest tests/integration --run-integration
```

CI runs this automatically as the `integration-mock` job — no secrets
needed.

## Live tests against the real Google API

```bash
export GBP_CLIENT_ID=...
export GBP_CLIENT_SECRET=...
export GBP_REFRESH_TOKEN=...
export GBP_TEST_ACCOUNT_ID=accounts/1234567890   # optional but enables more tests

pytest tests/integration --run-live
```

These hit Google's real APIs with real credentials. They are **never** run
in CI — the secrets are not in any CI environment, and the live API has
quotas you don't want a CI run burning.

### Mutating live tests

The default live suite is read-only. There is one PATCH test, and it only
runs when you explicitly opt in with two extra env vars:

```bash
export GBP_LIVE_PATCH_LOCATION=locations/9876543210
export GBP_LIVE_PATCH_VALUE=https://example.com

pytest tests/integration --run-live
```

Even with those set the test uses `validate_only=True`, so the call hits
the API but **does not** modify the profile. There is no test in this
repository that writes to a real Business Profile location — that is
intentional.

## Coverage

`pytest` is configured (via `pyproject.toml`) to print a coverage report
after every run. The `httpx` transport adapter is partially uncovered by
design — it's exercised by the integration suite, not the unit suite.

```text
TOTAL                                        293     23    92%
============================== 27 passed in 0.10s ==============================
```

## Adding tests for a new resource

1. Add the resource class under `src/gbp_connector/resources/`.
2. Add a unit test in `tests/` using `FakeHttpClient` for HTTP and
   `FakeAuth` for the bearer token. Assert what was sent (URL, headers,
   body) and what was parsed back into a model.
3. If the resource is in the OpenAPI spec, add a one-line test in
   `tests/integration/test_mock_prism.py` that calls the new method against
   the mock to catch spec drift.
4. Only add a `live` test if there's behavior the mock can't simulate
   (e.g. a quota-dependent flow). Live tests are not free.
