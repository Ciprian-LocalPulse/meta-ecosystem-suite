import pytest
from meta_ecosystem_suite.metrics_migrator.normalizer import MetricsNormalizer

def test_normalize_insights():
    raw_data = {"impressions": 15000, "reach": 4500}
    normalized_data = MetricsNormalizer.normalize_insights(raw_data)
    assert normalized_data["unified_meta_metrics"]["total_views"] == 15000
    assert normalized_data["unified_meta_metrics"]["unique_viewers"] == 4500
    assert normalized_data["unified_meta_metrics"]["view_frequency"] == 3.33
    assert normalized_data["legacy_metrics"]["impressions"] == 15000
    assert normalized_data["legacy_metrics"]["reach"] == 4500
    assert normalized_data["schema_version"] == "v19.0_UNIFIED"

def test_normalize_insights_zero_reach():
    raw_data = {"impressions": 1000, "reach": 0}
    normalized_data = MetricsNormalizer.normalize_insights(raw_data)
    assert normalized_data["unified_meta_metrics"]["total_views"] == 1000
    assert normalized_data["unified_meta_metrics"]["unique_viewers"] == 0
    assert normalized_data["unified_meta_metrics"]["view_frequency"] == 0.0
