import httpx
import asyncio
from typing import Dict, Any

class MetaStatusSentinel:
    """Monitorizarea latenței API-urilor Meta și trimiterea de alerte."""

    GRAPH_ENDPOINT = "https://graph.facebook.com/v19.0/debug_token"

    async def check_api_latency(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                start = asyncio.get_event_loop().time()
                response = await client.get("https://www.facebook.com/api/graphql/", timeout=5.0)
                latency_ms = round((asyncio.get_event_loop().time() - start) * 1000, 2)
                
                return {
                    "status": "HEALTHY" if response.status_code < 500 else "DEGRADED",
                    "latency_ms": latency_ms,
                    "http_code": response.status_code
                }
            except Exception as e:
                return {
                    "status": "OUTAGE",
                    "latency_ms": -1,
                    "error": str(e)
                }
