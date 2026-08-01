"""Client for TikTok's Commercial Content API (Research API v2),
TikTok's equivalent of Meta's Ad Library API for EU DSA transparency.

Reference: https://developers.tiktok.com/doc/commercial-content-api-getting-started
Endpoint used here: POST /v2/research/adlib/ad/query/

Two notable differences from Meta's Ad Library API that matter for
this codebase:

1. **Auth is a Bearer token in the Authorization header**, not a
   query param. This is the pattern SECURITY.md flags as a risk for
   Meta's client (`access_token` leaking into access/proxy logs) —
   TikTok's API doesn't have that problem by design.
2. **Pagination is POST-body-driven** via an opaque `search_id`
   cursor returned in the response, rather than a fully-formed `next`
   URL like Meta's `paging.next`.

This client requires a TikTok for Developers Commercial Content API
application to be approved (see TIKTOK_CLIENT_KEY / TIKTOK_ACCESS_TOKEN
in config.py) — access isn't self-serve the way Meta's is.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from meta_ecosystem_suite.config import settings
from meta_ecosystem_suite.http import get_client, with_retries

logger = logging.getLogger(__name__)

DEFAULT_AD_FIELDS: list[str] = ["ad", "ad_group"]

# TikTok requires an explicit published-date range per query; default
# to the same 90-day lookback the Status Sentinel / DSA reports assume
# elsewhere unless the caller overrides it.
DEFAULT_LOOKBACK_DAYS = 90


class TikTokAdLibraryClient:
    """Extracts raw records from TikTok's Commercial Content Library."""

    ENDPOINT = "https://open.tiktokapis.com/v2/research/adlib/ad/query/"

    def __init__(self, access_token: str | None = None, lookback_days: int = DEFAULT_LOOKBACK_DAYS):
        self.access_token = access_token or settings.TIKTOK_ACCESS_TOKEN
        self.lookback_days = lookback_days

    def _date_range(self) -> dict[str, str]:
        today = datetime.now(UTC)
        start = today - timedelta(days=self.lookback_days)
        return {"min": start.strftime("%Y%m%d"), "max": today.strftime("%Y%m%d")}

    async def fetch_ads(
        self,
        search_terms: str,
        ad_reached_countries: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Fetch ads matching `search_terms`, paginating via `search_id`
        until either `limit` records are collected or TikTok reports
        `has_more: false`.

        TikTok's `filters.country` only accepts a single country code
        per query (unlike Meta's comma-joined list), so only the first
        entry of `ad_reached_countries` is honored; a warning is logged
        if more than one was passed so callers doing multi-country
        audits notice rather than silently getting partial coverage.
        """
        countries = ad_reached_countries or ["EU"]
        if len(countries) > 1:
            logger.warning(
                "TikTok Commercial Content API filters by a single country per query; "
                "using '%s' and ignoring %s. Run one call per country for full coverage.",
                countries[0],
                countries[1:],
            )

        base_filters: dict[str, Any] = {
            "ad_published_date_range": self._date_range(),
            "country": countries[0],
        }

        client = get_client()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        @with_retries()
        async def query_page(body: dict[str, Any]):
            response = await client.post(
                self.ENDPOINT,
                params={"fields": ",".join(DEFAULT_AD_FIELDS)},
                json=body,
                headers=headers,
                timeout=20.0,
            )
            response.raise_for_status()
            return response

        results: list[dict[str, Any]] = []
        search_id: str | None = None
        has_more = True

        while has_more and len(results) < limit:
            body: dict[str, Any] = {
                "filters": base_filters,
                "search_term": search_terms,
                "max_count": min(limit - len(results), 100),
            }
            if search_id:
                body["search_id"] = search_id

            logger.debug("Fetching TikTok Commercial Content page (collected so far: %d)", len(results))
            response = await query_page(body)
            payload = response.json().get("data", {})

            page_records = payload.get("ads", [])
            results.extend(page_records)
            logger.info(
                "TikTok Commercial Content page returned %d records (total=%d)",
                len(page_records),
                len(results),
            )

            has_more = bool(payload.get("has_more", False))
            search_id = payload.get("search_id")

        return results[:limit]
