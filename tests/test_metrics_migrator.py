from meta_ecosystem_suite.metrics_migrator.mappings import LEGACY_TO_UNIFIED, UNIFIED_TO_LEGACY
from meta_ecosystem_suite.metrics_migrator.normalizer import MetricsNormalizer


def test_normalize_basic():
    result = MetricsNormalizer.normalize_insights({"impressions": 1000, "reach": 500})
    assert result["unified_meta_metrics"]["total_views"] == 1000
    assert result["unified_meta_metrics"]["unique_viewers"] == 500
    assert result["unified_meta_metrics"]["view_frequency"] == 2.0


def test_normalize_zero_viewers_no_divide_error():
    result = MetricsNormalizer.normalize_insights({"impressions": 0, "reach": 0})
    assert result["unified_meta_metrics"]["view_frequency"] == 0.0


def test_normalize_prefers_unified_fields_when_present():
    result = MetricsNormalizer.normalize_insights({"impressions": 100, "reach": 50, "views": 200, "viewers": 80})
    assert result["unified_meta_metrics"]["total_views"] == 200
    assert result["unified_meta_metrics"]["unique_viewers"] == 80


def test_batch_normalize():
    rows = [{"impressions": 10, "reach": 5}, {"impressions": 20, "reach": 10}]
    results = MetricsNormalizer.batch_normalize(rows)
    assert len(results) == 2
    assert results[1]["unified_meta_metrics"]["total_views"] == 20


def test_mapping_dictionaries_are_inverses():
    for legacy, unified in LEGACY_TO_UNIFIED.items():
        assert UNIFIED_TO_LEGACY[unified] == legacy
