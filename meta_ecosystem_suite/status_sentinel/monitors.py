"""Individual health-check probes used by the Status Sentinel."""

from dataclasses import dataclass
from typing import Callable, Awaitable

import httpx


@dataclass
class ProbeResult:
    name: str
    status: str  # HEALTHY | DEGRADED | OUTAGE
    latency_ms: float
    detail: str = ""


async def http_probe(name: str, url: str, timeout: float = 5.0) -> ProbeResult:
    """Generic HTTP latency/status probe."""
    import time

    async with httpx.AsyncClient() as client:
        start = time.monotonic()
        try:
            response = await client.get(url, timeout=timeout)
            latency_ms = round((time.monotonic() - start) * 1000, 2)
            status = "HEALTHY" if response.status_code < 500 else "DEGRADED"
            return ProbeResult(name=name, status=status, latency_ms=latency_ms, detail=f"HTTP {response.status_code}")
        except httpx.RequestError as exc:
            latency_ms = round((time.monotonic() - start) * 1000, 2)
            return ProbeResult(name=name, status="OUTAGE", latency_ms=latency_ms, detail=str(exc))


# Registry of endpoints monitored by default. Extend freely.
DEFAULT_PROBES: dict[str, str] = {
    "graph_api": "https://graph.facebook.com",
    "marketing_api": "https://graph.facebook.com/v19.0",
    "ad_library": "https://www.facebook.com/ads/library",
}
