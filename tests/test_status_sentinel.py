import httpx
import pytest
import respx

from meta_ecosystem_suite.status_sentinel.notifier import Notifier
from meta_ecosystem_suite.status_sentinel.sentinel import MetaStatusSentinel


@pytest.mark.asyncio
@respx.mock
async def test_check_api_latency_returns_expected_keys():
    respx.get("https://graph.facebook.com").mock(return_value=httpx.Response(200))
    sentinel = MetaStatusSentinel(probes={"graph_api": "https://graph.facebook.com"})
    result = await sentinel.check_api_latency("graph_api")
    assert set(result.keys()) == {"status", "latency_ms", "detail"}
    assert result["status"] == "HEALTHY"


@pytest.mark.asyncio
@respx.mock
async def test_check_api_latency_reports_degraded_on_5xx():
    respx.get("https://graph.facebook.com").mock(return_value=httpx.Response(503))
    sentinel = MetaStatusSentinel(probes={"graph_api": "https://graph.facebook.com"})
    result = await sentinel.check_api_latency("graph_api")
    assert result["status"] == "DEGRADED"
    assert "503" in result["detail"]


@pytest.mark.asyncio
@respx.mock
async def test_check_api_latency_reports_outage_on_connection_error():
    respx.get("https://graph.facebook.com").mock(side_effect=httpx.ConnectError("boom"))
    sentinel = MetaStatusSentinel(probes={"graph_api": "https://graph.facebook.com"})
    result = await sentinel.check_api_latency("graph_api")
    assert result["status"] == "OUTAGE"


@pytest.mark.asyncio
@respx.mock
async def test_run_all_covers_every_probe():
    respx.get("https://graph.facebook.com").mock(return_value=httpx.Response(200))
    respx.get("https://www.facebook.com").mock(return_value=httpx.Response(200))
    probes = {"a": "https://graph.facebook.com", "b": "https://www.facebook.com"}
    sentinel = MetaStatusSentinel(probes=probes)
    results = await sentinel.run_all(notify_on_issue=False)
    assert {r["name"] for r in results} == set(probes.keys())
    assert all(r["status"] == "HEALTHY" for r in results)


def test_notifier_format_alert_empty_when_all_healthy():
    notifier = Notifier()
    payload = [{"name": "graph_api", "status": "HEALTHY", "latency_ms": 12.3, "detail": "HTTP 200"}]
    assert notifier.format_alert(payload) == ""


def test_notifier_format_alert_lists_unhealthy_probes():
    notifier = Notifier()
    payload = [{"name": "graph_api", "status": "OUTAGE", "latency_ms": -1, "detail": "timeout"}]
    alert = notifier.format_alert(payload)
    assert "graph_api" in alert
    assert "OUTAGE" in alert
