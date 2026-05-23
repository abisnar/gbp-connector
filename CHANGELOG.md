# Changelog

All notable changes to this project will be documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-05-22

First public release.

### Added
- `GoogleBusinessProfileConnector` facade with `AccountsResource` and
  `LocationsResource`.
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
  `docs/oauth-setup.md`, `docs/releasing.md`, `CONTRIBUTING.md`, plus
  runnable scripts in `examples/`.
- CI: lint, type-check, unit tests on Python 3.11/3.12/3.13,
  Prism-mock integration tests, OpenAPI lint, gitleaks secret scan.
- Release pipeline: tag-driven `release.yml` builds wheel + sdist, publishes
  to PyPI via OIDC Trusted Publishing, and attaches the artifacts to a
  GitHub Release with notes pulled from this file.
- Versioning via `hatch-vcs` — the package version is derived from the git
  tag, so there's no version string to keep in sync by hand.
