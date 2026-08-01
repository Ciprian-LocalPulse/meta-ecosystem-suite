"""Registers TikTok as a platform in the multi-platform DSA auditor."""

from meta_ecosystem_suite.platforms.base import PlatformSpec, register_platform
from meta_ecosystem_suite.platforms.tiktok.client import TikTokAdLibraryClient
from meta_ecosystem_suite.platforms.tiktok.transformer import TikTokDSATransformer

register_platform(
    PlatformSpec(name="tiktok", client_factory=TikTokAdLibraryClient, transformer=TikTokDSATransformer)
)
