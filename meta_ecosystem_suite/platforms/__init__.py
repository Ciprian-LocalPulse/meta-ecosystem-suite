"""Multi-platform DSA ad-transparency auditing.

Importing this package registers every supported platform (currently
`meta` and `tiktok`) via their side-effecting `__init__.py` modules.
Adding a new platform means adding a new subpackage here that calls
`register_platform(...)` — nothing else in the codebase needs to
change.
"""

from meta_ecosystem_suite.dsa_auditor.schema import DSAAdRecord

# Side-effecting imports: each of these calls register_platform() at
# module load time. Order doesn't matter, but both must be imported
# before get_platform()/available_platforms() are used.
from meta_ecosystem_suite.platforms import meta as _meta  # noqa: F401
from meta_ecosystem_suite.platforms import tiktok as _tiktok  # noqa: F401
from meta_ecosystem_suite.platforms.base import available_platforms, get_platform


async def run_dsa_audit(
    platform: str,
    search_terms: str,
    countries: list[str] | None = None,
    limit: int = 100,
) -> list[DSAAdRecord]:
    """Fetch + normalize ads from any registered platform.

    This is the platform-agnostic replacement for wiring
    `AdLibraryExtractor` + `DSATransformer` together by hand — the
    CLI (and any future orchestration, e.g. a scheduled multi-platform
    sweep) calls this instead of importing a specific platform.
    """
    spec = get_platform(platform)
    client = spec.build_client()
    raw_ads = await client.fetch_ads(search_terms, ad_reached_countries=countries, limit=limit)
    return spec.transformer.transform_batch(raw_ads)


__all__ = ["DSAAdRecord", "available_platforms", "get_platform", "run_dsa_audit"]
