import pytest

from meta_ecosystem_suite.status_sentinel.sentinel import (
    MetaStatusSentinel,
)


@pytest.mark.asyncio
async def test_check_api_latency_healthy(mocker):
    mocker.patch(
        "httpx.AsyncClient.get",
        return_value=mocker.Mock(status_code=200),
    )

    sentinel = MetaStatusSentinel()

    result = await sentinel.check_api_latency()

    assert result["status"] == "HEALTHY"
    assert result["http_code"] == 200
    assert result["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_check_api_latency_degraded(mocker):
    mocker.patch(
        "httpx.AsyncClient.get",
        return_value=mocker.Mock(status_code=500),
    )

    sentinel = MetaStatusSentinel()

    result = await sentinel.check_api_latency()

    assert result["status"] == "DEGRADED"
    assert result["http_code"] == 500
    assert result["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_check_api_latency_outage(mocker):
    mocker.patch(
        "httpx.AsyncClient.get",
        side_effect=Exception("Connection Error"),
    )

    sentinel = MetaStatusSentinel()

    result = await sentinel.check_api_latency()

    assert result["status"] == "OUTAGE"
    assert result["latency_ms"] == -1
    assert "Connection Error" in result["error"]
