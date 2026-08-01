"""Tests for GraphAPIClient. Previously untested; all calls here are
mocked with respx so nothing touches the real Graph API.
"""

import httpx
import pytest
import respx

from meta_ecosystem_suite.metrics_migrator.graph_client import GraphAPIClient

INSIGHTS_URL = "https://graph.facebook.com/v19.0/12345/insights"


@pytest.mark.asyncio
@respx.mock
async def test_get_insights_returns_first_row():
    respx.get(INSIGHTS_URL).mock(
        return_value=httpx.Response(200, json={"data": [{"impressions": "100", "reach": "50"}]})
    )
    client = GraphAPIClient(access_token="fake-token", api_version="v19.0")
    result = await client.get_insights("12345")
    assert result == {"impressions": "100", "reach": "50"}


@pytest.mark.asyncio
@respx.mock
async def test_get_insights_returns_empty_dict_when_no_data():
    respx.get(INSIGHTS_URL).mock(return_value=httpx.Response(200, json={"data": []}))
    client = GraphAPIClient(access_token="fake-token", api_version="v19.0")
    result = await client.get_insights("12345")
    assert result == {}


@pytest.mark.asyncio
@respx.mock
async def test_get_insights_retries_on_server_error():
    route = respx.get(INSIGHTS_URL).mock(
        side_effect=[
            httpx.Response(500),
            httpx.Response(200, json={"data": [{"impressions": "10"}]}),
        ]
    )
    client = GraphAPIClient(access_token="fake-token", api_version="v19.0")
    result = await client.get_insights("12345")
    assert result == {"impressions": "10"}
    assert route.call_count == 2


@pytest.mark.asyncio
@respx.mock
async def test_get_insights_does_not_retry_on_auth_error():
    route = respx.get(INSIGHTS_URL).mock(return_value=httpx.Response(401, json={"error": "bad token"}))
    client = GraphAPIClient(access_token="bad-token", api_version="v19.0")
    with pytest.raises(httpx.HTTPStatusError):
        await client.get_insights("12345")
    assert route.call_count == 1
