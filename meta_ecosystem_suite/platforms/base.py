"""Platform abstraction layer.

The DSA auditor originally spoke only to Meta's Ad Library API. Every
"Very Large Online Platform" under the EU DSA has to run an
equivalent ad-transparency repository (Meta's Ad Library, TikTok's
Commercial Content Library, etc.), so the extraction + normalization
pipeline is the same shape across platforms even though each one's
wire format is different.

This module defines that shared shape as a `Protocol` (structural
typing — no inheritance required) plus a small registry so the CLI
and orchestration code can do `get_platform("tiktok")` instead of
importing platform-specific classes directly.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from meta_ecosystem_suite.dsa_auditor.schema import DSAAdRecord


@runtime_checkable
class AdLibraryClient(Protocol):
    """Structural interface every platform's ad-library client satisfies.

    Implementations are NOT required to subclass this — any object
    with an async `fetch_ads(...)` matching this signature qualifies,
    which is why `dsa_auditor.extractor.AdLibraryExtractor` (written
    before this abstraction existed) satisfies it unmodified.
    """

    async def fetch_ads(
        self,
        search_terms: str,
        ad_reached_countries: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]: ...


class DSARecordTransformer(Protocol):
    """Structural interface for turning one platform's raw ad dict
    into the common `DSAAdRecord` schema."""

    @classmethod
    def transform_batch(cls, raw_records: list[dict[str, Any]]) -> list[DSAAdRecord]: ...


class PlatformSpec:
    """Bundles a platform's client + transformer + human-readable name."""

    def __init__(self, name: str, client_factory: type, transformer: DSARecordTransformer):
        self.name = name
        self.client_factory = client_factory
        self.transformer = transformer

    def build_client(self) -> AdLibraryClient:
        return self.client_factory()


_REGISTRY: dict[str, PlatformSpec] = {}


def register_platform(spec: PlatformSpec) -> None:
    _REGISTRY[spec.name] = spec


def get_platform(name: str) -> PlatformSpec:
    try:
        return _REGISTRY[name]
    except KeyError:
        available = ", ".join(sorted(_REGISTRY)) or "(none registered)"
        raise ValueError(f"Unknown ad platform '{name}'. Available: {available}") from None


def available_platforms() -> list[str]:
    return sorted(_REGISTRY)
