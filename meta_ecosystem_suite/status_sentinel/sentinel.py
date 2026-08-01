"""Async health-monitoring engine that runs all registered probes
concurrently and dispatches alerts for any degraded/outage results.
"""

import asyncio
from typing import Any

from meta_ecosystem_suite.status_sentinel.monitors import DEFAULT_PROBES, http_probe
from meta_ecosystem_suite.status_sentinel.notifier import Notifier


class MetaStatusSentinel:
    """Monitors Meta API endpoint latency/health and raises alerts on regressions."""

    def __init__(self, probes: dict[str, str] | None = None):
        self.probes = probes or DEFAULT_PROBES
        self.notifier = Notifier()

    async def check_api_latency(self, name: str = "graph_api") -> dict[str, Any]:
        """Backwards-compatible single-endpoint check."""
        url = self.probes.get(name, self.probes["graph_api"])
        result = await http_probe(name, url)
        return {"status": result.status, "latency_ms": result.latency_ms, "detail": result.detail}

    async def run_all(self, notify_on_issue: bool = True) -> list[dict[str, Any]]:
        tasks = [http_probe(name, url) for name, url in self.probes.items()]
        results = await asyncio.gather(*tasks)
        payload = [
            {"name": r.name, "status": r.status, "latency_ms": r.latency_ms, "detail": r.detail} for r in results
        ]

        if notify_on_issue:
            alert_text = self.notifier.format_alert(payload)
            if alert_text:
                await self.notifier.send_slack(alert_text)

        return payload
