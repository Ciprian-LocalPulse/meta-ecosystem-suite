"""
Rule definitions for Meta Advertising Policies and AI-content
disclosure requirements (Meta Ads Policy 4.3 - Personal Attributes,
and the 2024+ AI-Generated Content Disclosure requirements).

Each rule is intentionally kept as data (not hard-coded logic) so
that the rule set can be extended, translated, or loaded from an
external JSON/YAML source without touching the linter engine.
"""

from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class Rule:
    code: str
    severity: Severity
    description: str


# --- Meta Ads Policy 4.3: Personal Attributes -----------------------------
# Ads must not assert or imply a user's personal attributes (health,
# financial status, sexual orientation, etc.) directly at the reader.
PERSONAL_ATTRIBUTE_PATTERNS: list[str] = [
    r"are\s+you\s+(depressed|sick|in\s+debt|struggling)\??",
    r"looking\s+for\s+treatment\s+for",
    r"suffering\s+from",
    r"are\s+you\s+(poor|lonely|single)\??",
    r"diagnosed\s+with",
    r"your\s+(disease|disorder|addiction)",
]

# --- Unverified / exaggerated claims ---------------------------------------
UNVERIFIED_CLAIM_PHRASES: list[str] = [
    "100% guaranteed",
    "guaranteed results",
    "miracle cure",
    "risk-free",
    "no risk",
]

RULES: dict[str, Rule] = {
    "META_AI_DISCLOSURE_REQUIRED": Rule(
        code="META_AI_DISCLOSURE_REQUIRED",
        severity=Severity.HIGH,
        description="AI-generated ad creative must carry Meta's mandatory transparency label.",
    ),
    "META_PERSONAL_ATTRIBUTES_4_3": Rule(
        code="META_PERSONAL_ATTRIBUTES_4_3",
        severity=Severity.CRITICAL,
        description="Ad copy directly asserts or implies a viewer's personal attributes.",
    ),
    "META_UNVERIFIED_CLAIMS": Rule(
        code="META_UNVERIFIED_CLAIMS",
        severity=Severity.MEDIUM,
        description="Ad copy contains unverifiable or exaggerated performance claims.",
    ),
    "META_LANDING_PAGE_MISMATCH": Rule(
        code="META_LANDING_PAGE_MISMATCH",
        severity=Severity.MEDIUM,
        description="Landing page destination does not match the advertised offer.",
    ),
}
