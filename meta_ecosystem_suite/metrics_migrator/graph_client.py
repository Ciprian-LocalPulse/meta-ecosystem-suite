"""Thin async wrapper around the Meta Graph API (Marketing API v19.0+)
used to pull raw insights data for a given ad object.
"""

import logging
from typing import Any

from meta_ecosystem_suite.config import settings
from meta_ecosystem_suite.http import get_client, with_retries

logger = logging.getLogger(__name__)


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
        client = get_client()

        @with_retries()
        async def _get():
            response = await client.get(url, params=params, timeout=15.0)
            response.raise_for_status()
            return response

        logger.debug("Fetching insights for object_id=%s", object_id)
        response = await _get()
        payload = response.json()

        data = payload.get("data", [])
        logger.info("Insights fetch for object_id=%s returned %d row(s)", object_id, len(data))
        return data[0] if data else {}
