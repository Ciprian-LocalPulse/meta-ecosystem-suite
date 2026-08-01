"""Meta Ad Library API client used to pull raw ad transparency
records that will later be transformed into the EU DSA schema.
"""

import logging
from typing import Any

from meta_ecosystem_suite.config import settings
from meta_ecosystem_suite.http import get_client, with_retries

logger = logging.getLogger(__name__)

DEFAULT_AD_FIELDS: list[str] = [
    "id",
    "page_id",
    "ad_creative_bodies",
    "ad_creation_time",
    "ad_delivery_start_time",
    "ad_delivery_stop_time",
    "impressions",
    "spend",
    "currency",
    "demographic_distribution",
]


class AdLibraryExtractor:
    """Extracts raw records from the Meta Ad Library API."""

    ENDPOINT = "https://graph.facebook.com/{version}/ads_archive"

    def __init__(self, access_token: str | None = None, api_version: str | None = None):
        self.access_token = access_token or settings.META_ACCESS_TOKEN
        self.api_version = api_version or settings.META_GRAPH_VERSION

    async def fetch_ads(
        self,
        search_terms: str,
        ad_reached_countries: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        url = self.ENDPOINT.format(version=self.api_version)
        params = {
            "access_token": self.access_token,
            "search_terms": search_terms,
            "ad_reached_countries": ",".join(ad_reached_countries or ["EU"]),
            "ad_active_status": "ALL",
            "limit": limit,
            "fields": ",".join(DEFAULT_AD_FIELDS),
        }

        results: list[dict[str, Any]] = []
        client = get_client()
        next_url: str | None = url
        next_params: dict[str, Any] | None = params

        @with_retries()
        async def get_page(page_url: str, page_params: dict[str, Any] | None):
            response = await client.get(page_url, params=page_params, timeout=20.0)
            response.raise_for_status()
            return response

        while next_url and len(results) < limit:
            logger.debug("Fetching Ad Library page (collected so far: %d)", len(results))
            response = await get_page(next_url, next_params)
            payload = response.json()

            page_records = payload.get("data", [])
            results.extend(page_records)
            logger.info("Ad Library page returned %d records (total=%d)", len(page_records), len(results))

            next_url = payload.get("paging", {}).get("next")
            next_params = None  # `next` already contains encoded query params

        return results[:limit]
