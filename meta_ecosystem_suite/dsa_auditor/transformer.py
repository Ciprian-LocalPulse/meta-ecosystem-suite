"""Transforms raw Meta Ad Library records into validated DSA schema
objects (`DSAAdRecord`), applying safe defaults for missing or
range-obfuscated fields (Meta reports impressions/spend as ranges).
"""

from datetime import datetime
from typing import Any

from meta_ecosystem_suite.dsa_auditor.schema import DSAAdRecord, DSAAdvertiser, DSATargetingCriteria


class DSATransformer:
    """Maps raw Ad Library API dictionaries onto `DSAAdRecord` instances."""

    @staticmethod
    def _parse_range(value: Any) -> tuple[int | None, int | None]:
        if isinstance(value, dict):
            lower = value.get("lower_bound")
            upper = value.get("upper_bound")
            return (int(lower) if lower is not None else None, int(upper) if upper is not None else None)
        return None, None

    @classmethod
    def transform(cls, raw: dict[str, Any]) -> DSAAdRecord:
        impressions_min, impressions_max = cls._parse_range(raw.get("impressions"))
        spend_min, spend_max = cls._parse_range(raw.get("spend"))

        creative_bodies = raw.get("ad_creative_bodies") or [""]

        return DSAAdRecord(
            ad_id=str(raw["id"]),
            page_id=str(raw.get("page_id", "")),
            advertiser=DSAAdvertiser(name=raw.get("page_name", "Unknown")),
            creative_text=creative_bodies[0],
            ad_creation_time=datetime.fromisoformat(raw["ad_creation_time"]),
            ad_delivery_start_time=datetime.fromisoformat(raw["ad_delivery_start_time"]),
            ad_delivery_stop_time=(
                datetime.fromisoformat(raw["ad_delivery_stop_time"])
                if raw.get("ad_delivery_stop_time")
                else None
            ),
            impressions_range_min=impressions_min,
            impressions_range_max=impressions_max,
            spend_range_min=float(spend_min) if spend_min is not None else None,
            spend_range_max=float(spend_max) if spend_max is not None else None,
            currency=raw.get("currency", "EUR"),
            targeting=DSATargetingCriteria(),
        )

    @classmethod
    def transform_batch(cls, raw_records: list[dict[str, Any]]) -> list[DSAAdRecord]:
        transformed = []
        for record in raw_records:
            try:
                transformed.append(cls.transform(record))
            except (KeyError, ValueError):
                # Skip malformed records rather than failing the whole batch.
                continue
        return transformed
