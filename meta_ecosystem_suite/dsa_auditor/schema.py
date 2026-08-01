"""Pydantic models representing the EU Digital Services Act (DSA)
ad-transparency database schema (Article 39 requirements for
Very Large Online Platforms operating ad repositories).
"""

from datetime import datetime

from pydantic import BaseModel, Field


class DSAAdvertiser(BaseModel):
    name: str
    verified: bool = False
    payer_name: str | None = None


class DSATargetingCriteria(BaseModel):
    age_range: str | None = None
    genders: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    custom_audience: bool = False


class DSAAdRecord(BaseModel):
    """A single normalized record matching the EU DSA ad repository schema."""

    ad_id: str
    page_id: str
    advertiser: DSAAdvertiser
    creative_text: str
    ad_creation_time: datetime
    ad_delivery_start_time: datetime
    ad_delivery_stop_time: datetime | None = None
    impressions_range_min: int | None = None
    impressions_range_max: int | None = None
    spend_range_min: float | None = None
    spend_range_max: float | None = None
    currency: str = "EUR"
    targeting: DSATargetingCriteria = Field(default_factory=DSATargetingCriteria)
    is_ai_generated: bool = False
    ai_disclosure_present: bool = False
