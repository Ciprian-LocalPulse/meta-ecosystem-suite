"""Maps raw TikTok Commercial Content API records onto the same
`DSAAdRecord` schema Meta records use, so downstream reporting
(`DSAReporter`) and the DSA schema itself don't need to know which
platform an ad came from.

TikTok's public ad-library data is thinner than Meta's in a few
DSA-relevant ways that show up as `None` here rather than fabricated
values:

- No spend range is exposed (Meta reports ranges; TikTok reports none
  at all for the ad-query endpoint used here).
- No structured targeting breakdown is returned by this endpoint
  (audience reach numbers exist, but not age/gender/location
  targeting criteria the way Meta's `demographic_distribution` does).
- Ad creative body text isn't returned in a plain-text field the way
  Meta's `ad_creative_bodies` is — TikTok ads are primarily video, so
  `creative_text` falls back to the advertiser/brand name when no
  text field is present, rather than being left empty.
"""

from datetime import UTC, datetime
from typing import Any

from meta_ecosystem_suite.dsa_auditor.schema import DSAAdRecord, DSAAdvertiser, DSATargetingCriteria


class TikTokDSATransformer:
    """Maps raw TikTok Commercial Content dicts onto `DSAAdRecord` instances."""

    @staticmethod
    def _parse_date(value: Any) -> datetime | None:
        """TikTok dates come back as YYYYMMDD ints/strings, not ISO-8601."""
        if not value:
            return None
        return datetime.strptime(str(value), "%Y%m%d").replace(tzinfo=UTC)

    @classmethod
    def transform(cls, raw: dict[str, Any]) -> DSAAdRecord:
        ad = raw.get("ad", raw)  # tolerate either the nested `ad` shape or a flattened one

        advertiser_name = ad.get("advertiser_name") or ad.get("brand_name") or "Unknown"
        creation_time = cls._parse_date(ad.get("first_shown_date"))
        if creation_time is None:
            raise ValueError("TikTok ad record missing required first_shown_date")

        return DSAAdRecord(
            ad_id=str(ad["id"]),
            page_id=str(ad.get("advertiser_id", "")),
            advertiser=DSAAdvertiser(name=advertiser_name),
            creative_text=ad.get("creative_text") or advertiser_name,
            ad_creation_time=creation_time,
            ad_delivery_start_time=creation_time,
            ad_delivery_stop_time=cls._parse_date(ad.get("last_shown_date")),
            impressions_range_min=None,
            impressions_range_max=None,
            spend_range_min=None,
            spend_range_max=None,
            currency="EUR",
            targeting=DSATargetingCriteria(),
            platform="tiktok",
        )

    @classmethod
    def transform_batch(cls, raw_records: list[dict[str, Any]]) -> list[DSAAdRecord]:
        transformed = []
        for record in raw_records:
            try:
                transformed.append(cls.transform(record))
            except (KeyError, ValueError):
                # Skip malformed records rather than failing the whole batch,
                # matching DSATransformer's behavior for Meta records.
                continue
        return transformed
