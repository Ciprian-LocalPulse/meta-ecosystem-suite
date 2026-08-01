# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
once it reaches a 1.0 release.

## [Unreleased]

### Added

- **Multi-platform DSA auditor.** New `meta_ecosystem_suite/platforms/`
  package: a structural `AdLibraryClient` protocol + a small registry
  (`register_platform` / `get_platform` / `available_platforms`) so
  the DSA auditor isn't hard-wired to Meta anymore.
  - `platforms/tiktok/`: a real client for TikTok's Commercial
    Content API (Research API v2) — POST-based, `search_id` cursor
    pagination, Bearer-token auth in the `Authorization` header
    (notably safer than Meta's query-param token pattern), plus a
    transformer mapping TikTok's ad shape onto the same `DSAAdRecord`
    schema Meta records use.
  - `platforms/meta/`: thin registration wrapper around the existing
    `AdLibraryExtractor` / `DSATransformer` — no behavior change.
  - CLI: `meta-suite dsa audit ... --platform tiktok` (defaults to
    `meta` for backward compatibility). Unknown platform names exit
    with a clear error instead of an unhandled traceback.
  - `DSAAdRecord` gained a `platform` field (defaults to `"meta"`) so
    reports record provenance when auditing multiple platforms.
- Shared, connection-pooled `httpx.AsyncClient` and a `tenacity`-based
  retry/backoff decorator (`meta_ecosystem_suite/http.py`), replacing
  the previous pattern of creating a new client per request with no
  retry logic.
- Structured logging across `extractor.py`, `graph_client.py`,
  `monitors.py`, and the CLI (`--verbose` flag), replacing the
  previous silence outside of `rich`/`print` CLI output.
- Test coverage for previously-untested modules: `cli.py`,
  `dsa_auditor/extractor.py` (Ad Library pagination), and
  `metrics_migrator/graph_client.py`, including retry-on-429/5xx and
  no-retry-on-4xx behavior.
- `respx`-based mocking for every test that touches a Meta API
  endpoint, plus an autouse `tests/conftest.py` fixture that fails
  any un-mocked network call instead of silently depending on
  connectivity.
- `uv.lock` for fully reproducible dependency installs.
- Governance & security docs: `SECURITY.md`, `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `.github/CODEOWNERS`,
  `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`,
  `.github/dependabot.yml`.
- `.pre-commit-config.yaml` running `ruff`, `mypy`, `bandit`, and
  basic file hygiene hooks locally, plus a manual `pip-audit` hook.

### Changed

- All Meta API dependencies (`pydantic`, `httpx`, `typer`, etc.) now
  have explicit upper bounds in `pyproject.toml` instead of open-ended
  `>=` constraints.
- Removed the deprecated `typer[all]` extra in favor of plain `typer`.

### Fixed

- Network-dependent tests no longer require internet access or fail
  when run offline / behind a CI IP block.

## [0.1.0] — initial internal release

### Added

- DSA Compliance Auditor (`dsa_auditor/`): Ad Library extraction,
  transformation into the EU DSA schema, and JSON reporting.
- Metrics Migrator (`metrics_migrator/`): legacy → unified metrics
  normalization with a bidirectional field-mapping table.
- Ad Policy Linter (`policy_linter/`): AI-disclosure, personal
  attributes (Policy 4.3), and unverified-claims checks.
- Status Sentinel (`status_sentinel/`): async health/latency probes
  for Graph API, Marketing API, and Ad Library, with Slack alerting.
- Unified `meta-suite` CLI exposing all four modules.
