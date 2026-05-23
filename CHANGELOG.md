# Changelog

All notable changes to this project will be documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Initial library scaffold: `GoogleBusinessProfileConnector` facade with
  `AccountsResource` and `LocationsResource`.
- `OAuth2RefreshTokenProvider` with thread-safe caching and 60s expiry leeway.
- `StaticTokenProvider` for tests and "I already have a token" use cases.
- `HttpxClient` default transport; protocol-based `HttpClient` for substitution.
- Typed exception hierarchy: `GBPConnectorError`, `GBPApiError`,
  `AuthenticationError`, `ConfigurationError`, `NotFoundError`, `RateLimitError`.
- Pydantic models for `Account` and `Location` (with `extra="allow"` passthrough).
- OpenAPI 3.1 spec at `openapi/google-business-profile.yaml` describing the
  upstream API contract.
- Integration tests gated by `--run-integration` (Prism mock) and `--run-live`
  (real Google APIs) so the default `pytest` invocation stays offline.
- Docs: `docs/usage.md`, `docs/testing.md`, `docs/architecture.md`,
  `docs/oauth-setup.md`, `CONTRIBUTING.md`, plus runnable scripts in
  `examples/`.
- CI: lint, type-check, unit tests on Python 3.11/3.12/3.13,
  Prism-mock integration tests, OpenAPI lint, gitleaks secret scan.

### Fixed
- CI cache: `setup-uv` is now keyed off `pyproject.toml` instead of expecting
  a (deliberately absent) `uv.lock`.
