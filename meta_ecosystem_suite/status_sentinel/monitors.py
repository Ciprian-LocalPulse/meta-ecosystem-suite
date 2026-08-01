"""Individual health-check probes used by the Status Sentinel."""

import logging
from dataclasses import dataclass

import httpx

from meta_ecosystem_suite.http import get_client

logger = logging.getLogger(__name__)


@dataclass
class ProbeResult:
    name: str
    status: str  # HEALTHY | DEGRADED | OUTAGE
    latency_ms: float
    detail: str = ""


async def http_probe(name: str, url: str, timeout: float = 5.0) -> ProbeResult:
    """Generic HTTP latency/status probe.

    Deliberately does NOT retry: a probe exists to report real-time
    status, and retrying here would mask a genuine outage instead of
    surfacing it. Retries belong in the data-fetching clients
    (extractor.py, graph_client.py), not in the health check itself.
    """
    import time

    client = get_client()
    start = time.monotonic()
    try:
        response = await client.get(url, timeout=timeout)
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        status = "HEALTHY" if response.status_code < 500 else "DEGRADED"
        logger.info("Probe %s -> %s (%.2fms, HTTP %s)", name, status, latency_ms, response.status_code)
        return ProbeResult(name=name, status=status, latency_ms=latency_ms, detail=f"HTTP {response.status_code}")
    except httpx.RequestError as exc:
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        logger.warning("Probe %s -> OUTAGE (%.2fms): %s", name, latency_ms, exc)
        return ProbeResult(name=name, status="OUTAGE", latency_ms=latency_ms, detail=str(exc))


# Registry of endpoints monitored by default. Extend freely.
DEFAULT_PROBES: dict[str, str] = {
    "graph_api": "https://graph.facebook.com",
    "marketing_api": "https://graph.facebook.com/v19.0",
    "ad_library": "https://www.facebook.com/ads/library",
}
