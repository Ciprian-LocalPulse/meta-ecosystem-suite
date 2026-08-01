"""Field mapping dictionary between legacy Meta Insights metrics
and the unified Views/Viewers reporting schema introduced in
Graph API v19.0+.
"""

LEGACY_TO_UNIFIED: dict[str, str] = {
    "impressions": "total_views",
    "reach": "unique_viewers",
    "frequency": "view_frequency",
    "video_p25_watched_actions": "video_views_25pct",
    "video_p50_watched_actions": "video_views_50pct",
    "video_p75_watched_actions": "video_views_75pct",
    "video_p100_watched_actions": "video_views_complete",
    "unique_clicks": "unique_interactions",
    "clicks": "total_interactions",
}

UNIFIED_TO_LEGACY: dict[str, str] = {v: k for k, v in LEGACY_TO_UNIFIED.items()}

# Metrics that only exist in the unified schema (no legacy equivalent).
UNIFIED_ONLY_METRICS: list[str] = [
    "engaged_viewers",
    "view_through_conversions",
]
