from typing import Dict, Any

class MetricsNormalizer:
    """Conversia automată din metrici legacy (Reach/Impressions) în schema unificată Meta (Views/Viewers)."""

    @staticmethod
    def normalize_insights(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        impressions = int(raw_data.get("impressions", 0))
        reach = int(raw_data.get("reach", 0))
        
        # Mappings la noile metrici
        views = int(raw_data.get("views", impressions))
        viewers = int(raw_data.get("viewers", reach))
        
        frequency = round(views / viewers, 2) if viewers > 0 else 0.0

        return {
            "legacy_metrics": {
                "impressions": impressions,
                "reach": reach
            },
            "unified_meta_metrics": {
                "total_views": views,
                "unique_viewers": viewers,
                "view_frequency": frequency
            },
            "schema_version": "v19.0_UNIFIED"
        }
