# Legacy → Unified Metrics Mapping

Meta's Graph API v19.0+ introduced a unified reporting model built
around **Views** and **Viewers**, replacing the older **Impressions**
and **Reach** terminology across ads reporting surfaces. This table is
the canonical mapping used by `metrics_migrator/mappings.py`.

| Legacy field | Unified field | Notes |
| --- | --- | --- |
| `impressions` | `total_views` | Total number of times content was shown. |
| `reach` | `unique_viewers` | Distinct people who saw the content. |
| `frequency` | `view_frequency` | `total_views / unique_viewers`, computed if not supplied directly. |
| `video_p25_watched_actions` | `video_views_25pct` | Video watched to 25%. |
| `video_p50_watched_actions` | `video_views_50pct` | Video watched to 50%. |
| `video_p75_watched_actions` | `video_views_75pct` | Video watched to 75%. |
| `video_p100_watched_actions` | `video_views_complete` | Video watched to completion. |
| `unique_clicks` | `unique_interactions` | Distinct people who clicked. |
| `clicks` | `total_interactions` | Total click events. |

Fields with no legacy equivalent (`engaged_viewers`,
`view_through_conversions`) are exposed only in the unified schema —
see `UNIFIED_ONLY_METRICS` in `mappings.py`.

## Using the mapping programmatically

```python
from meta_ecosystem_suite.metrics_migrator.mappings import LEGACY_TO_UNIFIED

unified_field = LEGACY_TO_UNIFIED["impressions"]  # -> "total_views"
```
