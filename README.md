# MetaEcosystemSuite

<p align="center">
  <img src="assets/meta-ecosystem-suite.png" alt="MetaEcosystemSuite" width="800">
</p>

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Meta Graph API v19.0](https://img.shields.io/badge/Meta%20Graph%20API-v19.0-0866FF)](https://developers.facebook.com/)
[![EU DSA Compliant](https://img.shields.io/badge/EU%20DSA-Compliant-003399)](https://ec.europa.eu/)
[![Tests](https://github.com/Ciprian-LocalPulse/meta-ecosystem-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/Ciprian-LocalPulse/meta-ecosystem-suite/actions/workflows/ci.yml)

**MetaEcosystemSuite** is a proprietary engine that unifies four common pain points teams hit when building on the Meta (Facebook / Instagram) advertising ecosystem: EU DSA transparency reporting, legacy-to-unified metrics migration, pre-launch ad policy linting, and API health monitoring — all behind a single CLI and Python package.

---

## Why this exists

Meta's advertising stack keeps shifting under developers' feet: the Graph API renames metrics, the EU Digital Services Act imposes new ad-transparency obligations on platforms operating in the EU, and Meta's own ad policies (including newer AI-content disclosure rules) change often enough that manual review doesn't scale. MetaEcosystemSuite bundles the plumbing so you don't have to rebuild it for every project.

---

## Key Features

1. **DSA Compliance Auditor** — a multi-platform ETL pipeline that pulls records from an ad-transparency repository (Meta's Ad Library API, TikTok's Commercial Content API) and converts them into a common EU DSA ad-transparency schema (advertiser identity, targeting criteria, spend/impression ranges, AI-disclosure status). Adding a new platform is a matter of registering a client + transformer pair in `platforms/` — nothing else in the codebase needs to change.
2. **Metrics Migrator** — normalizes legacy insights fields (`impressions`, `reach`) into Meta's unified reporting model (`views`, `viewers`), with a full bidirectional field-mapping table.
3. **Ad Policy Linter** — a pre-launch validator that checks ad copy against Meta's Policy 4.3 (personal attributes), AI-generated content disclosure requirements, and common exaggerated-claim patterns.
4. **Status Sentinel** — an async monitor that checks Graph API / Marketing API / Ad Library latency and health concurrently, with Slack alerting on degradation.

Each module is independently usable as a Python library or through the unified `meta-suite` CLI.

---

## Installation

```bash
git clone https://github.com/Ciprian-LocalPulse/meta-ecosystem-suite.git
cd meta-ecosystem-suite
pip install -e .
```

Copy `.env.example` to `.env` and fill in your Meta App credentials before using anything that talks to the live Graph API (the linter and normalizer work fully offline).

```bash
cp .env.example .env
```

---

## Quickstart

### Lint an ad before launch

```bash
meta-suite lint "Are you struggling with debt? Try our app!" --is-ai
```

### Normalize legacy metrics

```bash
meta-suite metrics normalize --impressions 15000 --reach 4500
```

### Pull an EU DSA transparency report

```bash
# Meta (default platform)
meta-suite dsa audit "example brand" --countries EU --output reports/dsa_report.json

# TikTok — requires an approved Commercial Content API application (see .env.example)
meta-suite dsa audit "example brand" --platform tiktok --countries FR --output reports/tiktok_dsa_report.json
```

Run `meta-suite dsa audit --help` to see which platforms are currently registered.

### Check API health

```bash
meta-suite sentinel check
```

---

## Project layout

```
meta_ecosystem_suite/
├── config.py              # Pydantic Settings (env-driven)
├── cli.py                 # Unified Typer CLI entrypoint
├── http.py                 # Shared pooled HTTP client + retry/backoff
├── dsa_auditor/            # EU DSA transparency ETL (Meta-specific extractor/transformer/schema)
├── platforms/              # Multi-platform registry (meta, tiktok) — see below
├── metrics_migrator/        # Legacy -> unified metrics schema
├── policy_linter/          # Ad policy & AI disclosure linter
└── status_sentinel/         # Async API health monitor
```

`platforms/` is what makes `dsa audit --platform tiktok` work: each subpackage (`platforms/meta/`, `platforms/tiktok/`) registers a client + transformer pair against the platform-agnostic `DSAAdRecord` schema in `dsa_auditor/schema.py`. `platforms.run_dsa_audit(platform, ...)` is the single entrypoint the CLI calls; it doesn't know or care which platform-specific classes exist behind that name.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for a deeper walkthrough of how the modules fit together.

---

## Running tests

```bash
pip install -e ".[dev]"
pytest
```

---

## Docker

```bash
docker compose up --build
```

---

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design and module boundaries
- [`docs/DSA_COMPLIANCE.md`](docs/DSA_COMPLIANCE.md) — guide to EU DSA reporting requirements and how the auditor maps to them
- [`docs/METRICS_MAPPING.md`](docs/METRICS_MAPPING.md) — full legacy ↔ unified metrics conversion table

---

## Contributing

This is proprietary software (see [`LICENSE`](LICENSE)). Bug reports and feature suggestions are welcome via GitHub Issues. Pull requests may be submitted for review, but submission does not transfer copyright, and the repository owner retains full discretion over whether contributions are accepted or incorporated.

## Supporting the project

This project is developed and maintained independently. If it's useful to you, see [`FUNDING.md`](FUNDING.md) for ways to support ongoing development.

## License

All rights reserved. This Software is proprietary and is **not** open-source — viewing the public repository and its documentation is permitted, but copying, modifying, redistributing, or reusing any part of the code requires prior written authorization from the copyright holder. See [`LICENSE`](LICENSE) for the full terms.

## Author

Built and maintained by **Ciprian Stefan Plesca** ([@Ciprian-LocalPulse](https://github.com/Ciprian-LocalPulse)), independent researcher and developer under the LocalPulse brand.