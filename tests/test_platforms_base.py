import httpx
import pytest
import respx

from meta_ecosystem_suite.platforms import available_platforms, get_platform, run_dsa_audit
from meta_ecosystem_suite.platforms.base import PlatformSpec, register_platform


def test_meta_and_tiktok_are_registered():
    assert set(available_platforms()) == {"meta", "tiktok"}


def test_get_platform_returns_matching_spec():
    spec = get_platform("meta")
    assert spec.name == "meta"


def test_get_platform_raises_on_unknown_name():
    with pytest.raises(ValueError, match="Unknown ad platform"):
        get_platform("google_ads")


def test_register_platform_adds_new_entry():
    class FakeClient:
        async def fetch_ads(self, search_terms, ad_reached_countries=None, limit=100):
            return []

    class FakeTransformer:
        @classmethod
        def transform_batch(cls, raw_records):
            return []

    register_platform(PlatformSpec(name="_test_fake", client_factory=FakeClient, transformer=FakeTransformer))
    assert "_test_fake" in available_platforms()


@pytest.mark.asyncio
@respx.mock
async def test_run_dsa_audit_dispatches_to_meta():
    respx.get("https://graph.facebook.com/v19.0/ads_archive").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "1",
                        "page_id": "p1",
                        "page_name": "Acme",
                        "ad_creative_bodies": ["Buy shoes"],
                        "ad_creation_time": "2026-01-01T00:00:00+0000",
                        "ad_delivery_start_time": "2026-01-01T00:00:00+0000",
                    }
                ],
                "paging": {},
            },
        )
    )
    records = await run_dsa_audit("meta", "shoes", countries=["EU"], limit=10)
    assert len(records) == 1
    assert records[0].platform == "meta"
    assert records[0].ad_id == "1"


@pytest.mark.asyncio
async def test_run_dsa_audit_raises_on_unknown_platform():
    with pytest.raises(ValueError):
        await run_dsa_audit("google_ads", "shoes")
