# Changelog

All notable changes to this project will be documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Initial library scaffold: `GoogleBusinessProfileConnector` facade with
  `AccountsResource` and `LocationsResource`.
- `OAuth2RefreshTokenProvider` with thread-safe caching and 60s expiry leeway.
- `HttpxClient` default transport; protocol-based `HttpClient` for substitution.
- Typed exception hierarchy: `GBPConnectorError`, `GBPApiError`,
  `AuthenticationError`, `ConfigurationError`, `NotFoundError`, `RateLimitError`.
- Pydantic models for `Account` and `Location` (with `extra="allow"` passthrough).
- OpenAPI 3.1 spec at `openapi/google-business-profile.yaml` describing the
  upstream API contract.
- CI: lint, type-check, tests on Python 3.11/3.12/3.13, OpenAPI lint, gitleaks
  secret scan.
