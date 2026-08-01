from datetime import UTC, datetime

from meta_ecosystem_suite.platforms.tiktok.transformer import TikTokDSATransformer


def test_transform_maps_core_fields():
    raw = {
        "ad": {
            "id": "12345",
            "advertiser_id": "adv-1",
            "advertiser_name": "Acme Corp",
            "first_shown_date": "20260101",
            "last_shown_date": "20260115",
        }
    }
    record = TikTokDSATransformer.transform(raw)
    assert record.ad_id == "12345"
    assert record.page_id == "adv-1"
    assert record.advertiser.name == "Acme Corp"
    assert record.platform == "tiktok"
    assert record.ad_creation_time == datetime(2026, 1, 1, tzinfo=UTC)
    assert record.ad_delivery_stop_time == datetime(2026, 1, 15, tzinfo=UTC)


def test_transform_falls_back_to_advertiser_name_for_creative_text():
    raw = {"ad": {"id": "1", "advertiser_name": "Acme Corp", "first_shown_date": "20260101"}}
    record = TikTokDSATransformer.transform(raw)
    assert record.creative_text == "Acme Corp"


def test_transform_has_no_spend_or_impressions_data():
    raw = {"ad": {"id": "1", "advertiser_name": "Acme Corp", "first_shown_date": "20260101"}}
    record = TikTokDSATransformer.transform(raw)
    assert record.spend_range_min is None
    assert record.spend_range_max is None
    assert record.impressions_range_min is None
    assert record.impressions_range_max is None


def test_transform_batch_skips_records_missing_first_shown_date():
    rows = [
        {"ad": {"id": "1", "advertiser_name": "Acme"}},  # missing first_shown_date -> dropped
        {"ad": {"id": "2", "advertiser_name": "Acme", "first_shown_date": "20260101"}},
    ]
    results = TikTokDSATransformer.transform_batch(rows)
    assert len(results) == 1
    assert results[0].ad_id == "2"


def test_transform_tolerates_flattened_shape_without_nested_ad_key():
    raw = {"id": "1", "advertiser_name": "Acme", "first_shown_date": "20260101"}
    record = TikTokDSATransformer.transform(raw)
    assert record.ad_id == "1"
