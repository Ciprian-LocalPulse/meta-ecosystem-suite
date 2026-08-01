"""Alert dispatchers for the Status Sentinel (Slack webhook and
console/email fallback). Kept dependency-light: uses httpx directly
rather than a dedicated Slack SDK.
"""

from typing import Any

import httpx

from meta_ecosystem_suite.config import settings


class Notifier:
    """Sends alerts to configured channels when a probe degrades or fails."""

    async def send_slack(self, message: str) -> bool:
        if not settings.SLACK_WEBHOOK_URL:
            return False
        payload = {"text": message}
        async with httpx.AsyncClient() as client:
            response = await client.post(settings.SLACK_WEBHOOK_URL, json=payload, timeout=10.0)
            return response.status_code < 300

    def format_alert(self, probe_results: list[dict[str, Any]]) -> str:
        unhealthy = [p for p in probe_results if p["status"] != "HEALTHY"]
        if not unhealthy:
            return ""
        lines = [f"*MetaEcosystemSuite Status Alert* ({len(unhealthy)} issue(s) detected)"]
        for probe in unhealthy:
            lines.append(f"- `{probe['name']}`: *{probe['status']}* ({probe['latency_ms']}ms) — {probe.get('detail', '')}")
        return "\n".join(lines)
