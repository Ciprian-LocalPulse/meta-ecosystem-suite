"""Tests for AdLibraryExtractor: pagination, limit handling, and the
retry/backoff behavior added on top of the shared HTTP client.

Previously this module (arguably the most fragile piece of the
codebase — cursor-based pagination against a live external API) had
zero test coverage. All network calls here are mocked with respx;
nothing touches the real Meta Ad Library API.
"""

import httpx
import pytest
import respx

from meta_ecosystem_suite.dsa_auditor.extractor import AdLibraryExtractor

ENDPOINT = "https://graph.facebook.com/v19.0/ads_archive"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_ads_single_page():
    respx.get(ENDPOINT).mock(
        return_value=httpx.Response(200, json={"data": [{"id": "1"}, {"id": "2"}], "paging": {}})
    )
    extractor = AdLibraryExtractor(access_token="fake-token", api_version="v19.0")
    results = await extractor.fetch_ads("shoes", limit=100)
    assert [r["id"] for r in results] == ["1", "2"]


@pytest.mark.asyncio
@respx.mock
async def test_fetch_ads_follows_pagination_cursor():
    next_url = "https://graph.facebook.com/v19.0/ads_archive?after=cursor123"

    def responder(request: httpx.Request) -> httpx.Response:
        if "after" in request.url.params:
            return httpx.Response(200, json={"data": [{"id": "2"}], "paging": {}})
        return httpx.Response(200, json={"data": [{"id": "1"}], "paging": {"next": next_url}})

    respx.get(url__regex=r"https://graph\.facebook\.com/v19\.0/ads_archive.*").mock(side_effect=responder)

    extractor = AdLibraryExtractor(access_token="fake-token", api_version="v19.0")
    results = await extractor.fetch_ads("shoes", limit=100)
    assert [r["id"] for r in results] == ["1", "2"]


@pytest.mark.asyncio
@respx.mock
async def test_fetch_ads_stops_at_limit_even_with_more_pages():
    next_url = "https://graph.facebook.com/v19.0/ads_archive?after=cursor123"
    respx.get(ENDPOINT).mock(
        return_value=httpx.Response(
            200, json={"data": [{"id": "1"}, {"id": "2"}], "paging": {"next": next_url}}
        )
    )
    extractor = AdLibraryExtractor(access_token="fake-token", api_version="v19.0")
    results = await extractor.fetch_ads("shoes", limit=1)
    assert len(results) == 1


@pytest.mark.asyncio
@respx.mock
async def test_fetch_ads_retries_on_429_then_succeeds():
    route = respx.get(ENDPOINT).mock(
        side_effect=[
            httpx.Response(429, json={"error": "rate limited"}),
            httpx.Response(200, json={"data": [{"id": "1"}], "paging": {}}),
        ]
    )
    extractor = AdLibraryExtractor(access_token="fake-token", api_version="v19.0")
    results = await extractor.fetch_ads("shoes", limit=100)
    assert [r["id"] for r in results] == ["1"]
    assert route.call_count == 2


@pytest.mark.asyncio
@respx.mock
async def test_fetch_ads_does_not_retry_on_400_bad_request():
    route = respx.get(ENDPOINT).mock(return_value=httpx.Response(400, json={"error": "bad params"}))
    extractor = AdLibraryExtractor(access_token="fake-token", api_version="v19.0")
    with pytest.raises(httpx.HTTPStatusError):
        await extractor.fetch_ads("shoes", limit=100)
    assert route.call_count == 1
