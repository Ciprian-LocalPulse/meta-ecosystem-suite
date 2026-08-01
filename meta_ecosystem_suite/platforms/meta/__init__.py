"""Registers Meta as a platform in the multi-platform DSA auditor.

This is a thin adapter: `AdLibraryExtractor` and `DSATransformer`
already satisfy the shapes `platforms.base` expects, written before
this abstraction existed. Nothing about their behavior changes here.
"""

from meta_ecosystem_suite.dsa_auditor.extractor import AdLibraryExtractor
from meta_ecosystem_suite.dsa_auditor.transformer import DSATransformer
from meta_ecosystem_suite.platforms.base import PlatformSpec, register_platform

register_platform(PlatformSpec(name="meta", client_factory=AdLibraryExtractor, transformer=DSATransformer))
