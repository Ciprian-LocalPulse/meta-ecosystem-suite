"""Metrics Normalizer.

Converts legacy Meta Insights fields (Reach / Impressions) into the
unified reporting model (Views / Viewers) that Meta rolled out
alongside Graph API v19.0. Keeping both representations lets teams
migrate dashboards incrementally.
"""

from typing import Any


class MetricsNormalizer:
    """Normalizes raw Graph API insights payloads into a unified schema."""

    @staticmethod
    def normalize_insights(raw_data: dict[str, Any]) -> dict[str, Any]:
        impressions = int(raw_data.get("impressions", 0) or 0)
        reach = int(raw_data.get("reach", 0) or 0)

        views = int(raw_data.get("views", impressions) or impressions)
        viewers = int(raw_data.get("viewers", reach) or reach)

        frequency = round(views / viewers, 2) if viewers > 0 else 0.0

        return {
            "legacy_metrics": {
                "impressions": impressions,
                "reach": reach,
            },
            "unified_meta_metrics": {
                "total_views": views,
                "unique_viewers": viewers,
                "view_frequency": frequency,
            },
            "schema_version": "v19.0_UNIFIED",
        }

    @staticmethod
    def batch_normalize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [MetricsNormalizer.normalize_insights(row) for row in rows]
