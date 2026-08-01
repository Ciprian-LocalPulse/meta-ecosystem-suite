"""Shared HTTP plumbing: a reusable, connection-pooled client plus a
retry/backoff decorator tuned for Meta's Graph / Marketing / Ad Library
APIs (which return 429s and transient 5xx errors under normal load).

Every module that talks to a Meta endpoint should go through
`get_client()` and wrap its outbound calls with `@with_retries`
instead of instantiating its own `httpx.AsyncClient()` per request.
"""

from __future__ import annotations

import logging

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

logger = logging.getLogger("meta_ecosystem_suite.http")

# A single, process-wide async client reused across calls so we get
# connection pooling instead of a new TCP/TLS handshake per request.
_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    """Return the shared, connection-pooled AsyncClient, creating it lazily."""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            timeout=httpx.Timeout(20.0, connect=10.0),
        )
    return _client


async def aclose_client() -> None:
    """Close the shared client. Call this on application shutdown."""
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()
    _client = None


def _is_retryable(exc: BaseException) -> bool:
    """Retry on network-level failures and on 429 / 5xx HTTP responses.

    4xx errors other than 429 (bad token, bad params, etc.) are not
    retried since retrying them would just waste calls against Meta's
    rate limit budget for the same failure.
    """
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or status >= 500
    return False


def log_retry(retry_state) -> None:  # type: ignore[no-untyped-def]
    exc = retry_state.outcome.exception() if retry_state.outcome else None
    logger.warning(
        "Retrying Meta API call (attempt %s) after error: %s",
        retry_state.attempt_number,
        exc,
    )


def with_retries(max_attempts: int = 5):
    """Decorator factory applying exponential backoff with jitter.

    Retries up to `max_attempts` times on transport errors, HTTP 429
    (rate limit), and HTTP 5xx responses. All other exceptions
    (including 4xx auth/validation errors) propagate immediately.
    """
    return retry(
        reraise=True,
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential_jitter(initial=1, max=30),
        retry=retry_if_exception(_is_retryable),
        before_sleep=log_retry,
    )
