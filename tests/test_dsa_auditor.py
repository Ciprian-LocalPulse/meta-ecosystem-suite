from datetime import datetime, timezone

from meta_ecosystem_suite.dsa_auditor.reporter import DSAReporter
from meta_ecosystem_suite.dsa_auditor.schema import DSAAdRecord, DSAAdvertiser
from meta_ecosystem_suite.dsa_auditor.transformer import DSATransformer


def make_record(**overrides) -> DSAAdRecord:
    defaults = dict(
        ad_id="123",
        page_id="456",
        advertiser=DSAAdvertiser(name="Test Advertiser"),
        creative_text="Sample ad copy",
        ad_creation_time=datetime.now(timezone.utc),
        ad_delivery_start_time=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return DSAAdRecord(**defaults)


def test_transformer_parses_range_fields():
    raw = {
        "id": "1",
        "page_id": "2",
        "page_name": "Acme",
        "ad_creative_bodies": ["Buy now"],
        "ad_creation_time": "2026-01-01T00:00:00+00:00",
        "ad_delivery_start_time": "2026-01-02T00:00:00+00:00",
        "impressions": {"lower_bound": "1000", "upper_bound": "5000"},
        "spend": {"lower_bound": "100", "upper_bound": "500"},
        "currency": "EUR",
    }
    record = DSATransformer.transform(raw)
    assert record.impressions_range_min == 1000
    assert record.impressions_range_max == 5000
    assert record.spend_range_min == 100.0


def test_transform_batch_skips_malformed_records():
    good = {
        "id": "1",
        "page_id": "2",
        "ad_creative_bodies": ["ok"],
        "ad_creation_time": "2026-01-01T00:00:00+00:00",
        "ad_delivery_start_time": "2026-01-02T00:00:00+00:00",
    }
    bad = {"id": "2"}  # missing required fields
    records = DSATransformer.transform_batch([good, bad])
    assert len(records) == 1


def test_reporter_flags_ai_disclosure_violations():
    flagged = make_record(is_ai_generated=True, ai_disclosure_present=False)
    clean = make_record(ad_id="789", is_ai_generated=True, ai_disclosure_present=True)
    report = DSAReporter.build_report([flagged, clean])
    assert report["total_records"] == 2
    assert report["ai_disclosure_violations"] == 1


def test_write_json_creates_file(tmp_path):
    record = make_record()
    out_file = tmp_path / "reports" / "report.json"
    path = DSAReporter.write_json([record], str(out_file))
    assert out_file.exists()
    assert path == str(out_file)
