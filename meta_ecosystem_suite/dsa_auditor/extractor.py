"""Meta Ad Library API client used to pull raw ad transparency
records that will later be transformed into the EU DSA schema.
"""

from typing import Any

import httpx

from meta_ecosystem_suite.config import settings


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
            "fields": ",".join(
                [
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
            ),
        }

        results: list[dict[str, Any]] = []
        async with httpx.AsyncClient() as client:
            next_url: str | None = url
            next_params: dict[str, Any] | None = params

            while next_url and len(results) < limit:
                response = await client.get(next_url, params=next_params, timeout=20.0)
                response.raise_for_status()
                payload = response.json()

                results.extend(payload.get("data", []))
                next_url = payload.get("paging", {}).get("next")
                next_params = None  # `next` already contains encoded query params

        return results[:limit]
