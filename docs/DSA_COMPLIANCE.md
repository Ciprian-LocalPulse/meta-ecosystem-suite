# EU DSA Compliance Guide

The EU Digital Services Act (Regulation (EU) 2022/2065) requires Very
Large Online Platforms (VLOPs) — a designation that applies to Meta's
platforms — to maintain a publicly searchable repository of
advertisements, including who paid for them, who they targeted, and
how long they ran (Article 39).

This document explains how the `dsa_auditor` module maps onto those
requirements. It is not legal advice — consult qualified counsel for
compliance decisions.

## What the auditor captures

| DSA requirement | Field in `DSAAdRecord` |
| --- | --- |
| Ad content | `creative_text` |
| Advertiser identity | `advertiser.name`, `advertiser.payer_name` |
| Verification status | `advertiser.verified` |
| Campaign period | `ad_delivery_start_time`, `ad_delivery_stop_time` |
| Targeting parameters | `targeting.age_range`, `targeting.genders`, `targeting.locations`, `targeting.interests` |
| Reach / spend (ranged) | `impressions_range_min/max`, `spend_range_min/max` |
| AI-generated content flag | `is_ai_generated`, `ai_disclosure_present` |

## Typical workflow

```bash
meta-suite dsa audit "your brand name" --countries EU,RO --output reports/dsa_report.json
```

This pulls matching records from the Meta Ad Library API, validates
and normalizes them into the schema above, and writes a JSON report
that flags any AI-generated ad missing its required disclosure label.

## Known limitations

- Meta reports impressions and spend as **ranges**, not exact figures.
  The auditor preserves both bounds rather than guessing a midpoint.
- The Ad Library API's targeting fields are not always populated for
  every ad; `targeting` fields default to empty rather than failing
  the whole record.
- This tool reports on data Meta already exposes publicly through the
  Ad Library API — it does not independently verify advertiser
  identity or targeting accuracy.
