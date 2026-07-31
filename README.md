# MetaEcosystemSuite

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Meta Graph API v19.0](https://img.shields.io/badge/Meta%20Graph%20API-v19.0-0866FF)](https://developers.facebook.com/)
[![EU DSA Compliant](https://img.shields.io/badge/EU%20DSA-Compliant-003399)](https://ec.europa.eu/)

**MetaEcosystemSuite** is an open-source enterprise suite designed to solve compliance, analytics migration, ad linting, and API monitoring challenges within the Meta (Facebook / Instagram) ecosystem.

---

## Key Features

1. **DSA Compliance Auditor:** ETL pipeline converting Meta Ad Library API responses into the official EU Digital Services Act transparency schema.
2. **Metrics Migrator:** Normalizes legacy metrics (`Reach` / `Impressions`) into Meta's unified reporting model (`Views` / `Viewers`).
3. **Ad Policy Linter:** Pre-launch validator checking for AI disclosure tags, Policy 4.3 Personal Attribute violations, and Landing Page consistency.
4. **Status Sentinel:** Real-time async monitor tracking Graph API latencies and outages with Slack notification support.

---

## Quickstart

```bash
# Clone the repository
git clone [https://github.com/username/meta-ecosystem-suite.git](https://github.com/username/meta-ecosystem-suite.git)
cd meta-ecosystem-suite

# Install dependencies
pip install -e .

# Run Ad Policy Linter
meta-suite lint --text "Suferi de anxietate? Cumpără acum!" --is-ai True

# Normalize Metrics
meta-suite normalize --impressions 15000 --reach 4500
```

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
