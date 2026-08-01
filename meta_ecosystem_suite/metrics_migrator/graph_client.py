"""Thin async wrapper around the Meta Graph API (Marketing API v19.0+)
used to pull raw insights data for a given ad object.
"""

from typing import Any

import httpx

from meta_ecosystem_suite.config import settings


class GraphAPIClient:
    """Minimal async client for the `/insights` edge of the Graph API."""

    def __init__(self, access_token: str | None = None, api_version: str | None = None):
        self.access_token = access_token or settings.META_ACCESS_TOKEN
        self.api_version = api_version or settings.META_GRAPH_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    async def get_insights(
        self,
        object_id: str,
        fields: list[str] | None = None,
        date_preset: str = "last_30d",
    ) -> dict[str, Any]:
        fields = fields or [
            "impressions",
            "reach",
            "frequency",
            "clicks",
            "unique_clicks",
        ]
        params = {
            "access_token": self.access_token,
            "fields": ",".join(fields),
            "date_preset": date_preset,
        }
        url = f"{self.base_url}/{object_id}/insights"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=15.0)
            response.raise_for_status()
            payload = response.json()

        data = payload.get("data", [])
        return data[0] if data else {}
