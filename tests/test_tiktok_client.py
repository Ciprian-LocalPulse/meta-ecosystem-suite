"""Tests for TikTokAdLibraryClient. All calls are mocked with respx;
nothing touches TikTok's real Commercial Content API.
"""

import httpx
import pytest
import respx

from meta_ecosystem_suite.platforms.tiktok.client import TikTokAdLibraryClient

ENDPOINT = "https://open.tiktokapis.com/v2/research/adlib/ad/query/"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_ads_single_page():
    respx.post(ENDPOINT).mock(
        return_value=httpx.Response(
            200, json={"data": {"has_more": False, "search_id": None, "ads": [{"id": "1"}, {"id": "2"}]}}
        )
    )
    client = TikTokAdLibraryClient(access_token="fake-token")
    results = await client.fetch_ads("coffee", ad_reached_countries=["FR"], limit=100)
    assert [r["id"] for r in results] == ["1", "2"]


@pytest.mark.asyncio
@respx.mock
async def test_fetch_ads_sends_bearer_token_not_query_param():
    route = respx.post(ENDPOINT).mock(
        return_value=httpx.Response(200, json={"data": {"has_more": False, "ads": []}})
    )
    client = TikTokAdLibraryClient(access_token="secret-token-123")
    await client.fetch_ads("coffee", ad_reached_countries=["FR"])

    request = route.calls[0].request
    assert request.headers["authorization"] == "Bearer secret-token-123"
    assert "secret-token-123" not in str(request.url)  # never leaks into the URL/query string


@pytest.mark.asyncio
@respx.mock
async def test_fetch_ads_follows_search_id_pagination():
    def responder(request: httpx.Request) -> httpx.Response:
        import json

        body = json.loads(request.content)
        if "search_id" in body:
            return httpx.Response(200, json={"data": {"has_more": False, "ads": [{"id": "2"}]}})
        return httpx.Response(
            200, json={"data": {"has_more": True, "search_id": "cursor123", "ads": [{"id": "1"}]}}
        )

    respx.post(ENDPOINT).mock(side_effect=responder)
    client = TikTokAdLibraryClient(access_token="fake-token")
    results = await client.fetch_ads("coffee", ad_reached_countries=["FR"], limit=100)
    assert [r["id"] for r in results] == ["1", "2"]


@pytest.mark.asyncio
@respx.mock
async def test_fetch_ads_stops_at_limit_even_with_more_pages():
    respx.post(ENDPOINT).mock(
        return_value=httpx.Response(
            200, json={"data": {"has_more": True, "search_id": "cursor123", "ads": [{"id": "1"}, {"id": "2"}]}}
        )
    )
    client = TikTokAdLibraryClient(access_token="fake-token")
    results = await client.fetch_ads("coffee", ad_reached_countries=["FR"], limit=1)
    assert len(results) == 1


@pytest.mark.asyncio
@respx.mock
async def test_fetch_ads_retries_on_429_then_succeeds():
    route = respx.post(ENDPOINT).mock(
        side_effect=[
            httpx.Response(429, json={"error": "rate limited"}),
            httpx.Response(200, json={"data": {"has_more": False, "ads": [{"id": "1"}]}}),
        ]
    )
    client = TikTokAdLibraryClient(access_token="fake-token")
    results = await client.fetch_ads("coffee", ad_reached_countries=["FR"])
    assert [r["id"] for r in results] == ["1"]
    assert route.call_count == 2


@pytest.mark.asyncio
@respx.mock
async def test_fetch_ads_only_uses_first_country(caplog):
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json={"data": {"has_more": False, "ads": []}}))
    client = TikTokAdLibraryClient(access_token="fake-token")
    with caplog.at_level("WARNING"):
        await client.fetch_ads("coffee", ad_reached_countries=["FR", "DE", "IT"])
    assert "single country" in caplog.text
