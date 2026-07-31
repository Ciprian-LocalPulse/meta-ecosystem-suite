# Historical Conversion Tables

This document details the mapping and normalization process for converting legacy Meta advertising metrics into the unified Meta reporting model.

## Overview of Metrics Migration

Meta has transitioned its advertising reporting to a unified model, replacing legacy metrics like "Reach" and "Impressions" with "Viewers" and "Views," respectively. The `metrics_migrator` module in the MetaEcosystemSuite automates this conversion, ensuring historical data remains consistent and comparable with new reporting standards.

## The Normalization Process

The `MetricsNormalizer` class within `normalizer.py` handles the conversion logic. It takes raw data containing legacy metrics and outputs a structured dictionary containing both the legacy and unified metrics, along with calculated fields like "view_frequency."

### Mapping Table

The following table outlines the primary mappings between legacy and unified metrics:

| Legacy Metric | Unified Meta Metric | Description |
| :--- | :--- | :--- |
| Impressions | Views | The total number of times an ad was displayed on a screen. |
| Reach | Viewers | The estimated number of unique individuals who saw an ad at least once. |
| Frequency | View Frequency | The average number of times each unique viewer saw the ad (Views / Viewers). |

### Example Conversion

Consider a scenario where raw data indicates 15,000 impressions and a reach of 4,500. The `MetricsNormalizer` will process this as follows:

1.  **Extract Legacy Metrics:** Impressions = 15,000, Reach = 4,500.
2.  **Map to Unified Metrics:** Views = 15,000, Viewers = 4,500.
3.  **Calculate Derived Metrics:** View Frequency = Views / Viewers = 15,000 / 4,500 = 3.33.

The resulting output will be a structured dictionary:

```json
{
  "legacy_metrics": {
    "impressions": 15000,
    "reach": 4500
  },
  "unified_meta_metrics": {
    "total_views": 15000,
    "unique_viewers": 4500,
    "view_frequency": 3.33
  },
  "schema_version": "v19.0_UNIFIED"
}
```

## Implementation Details

The `mappings.py` file contains the comprehensive dictionary of field mappings, allowing for easy updates as Meta's API evolves. The `graph_client.py` provides a wrapper for interacting with the Meta Graph API v19.0+, facilitating the retrieval of raw metrics data.

## References

- [1] Meta Business Help Center: About Reach and Impressions - [https://www.facebook.com/business/help/739742622786392](https://www.facebook.com/business/help/739742622786392)
- [2] Meta Graph API Documentation - [https://developers.facebook.com/docs/graph-api](https://developers.facebook.com/docs/graph-api)
