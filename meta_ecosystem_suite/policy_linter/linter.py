"""Ad Policy & AI Content Linter.

Runs pre-launch checks against ad copy for:
  1. Missing AI-generated content disclosure
  2. Meta Ads Policy 4.3 (personal attributes) violations
  3. Unverified / exaggerated performance claims
  4. Basic readability red flags

The engine is deliberately data-driven (see `rules.py`) so new
checks can be added without modifying `AdPolicyLinter` itself.
"""

from typing import Any

from meta_ecosystem_suite.policy_linter.nlp_checker import NLPChecker
from meta_ecosystem_suite.policy_linter.rules import (
    PERSONAL_ATTRIBUTE_PATTERNS,
    RULES,
    UNVERIFIED_CLAIM_PHRASES,
)


class AdPolicyLinter:
    """Pre-launch validator for Meta advertising creative."""

    def __init__(self) -> None:
        self._checker = NLPChecker(
            patterns=PERSONAL_ATTRIBUTE_PATTERNS,
            phrases=UNVERIFIED_CLAIM_PHRASES,
        )

    def lint_ad(
        self,
        ad_text: str,
        is_ai_generated: bool = False,
        ai_disclosed: bool = False,
        landing_page_topic: str | None = None,
        ad_topic: str | None = None,
    ) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []

        # 1. AI disclosure requirement
        if is_ai_generated and not ai_disclosed:
            rule = RULES["META_AI_DISCLOSURE_REQUIRED"]
            violations.append({"rule": rule.code, "severity": rule.severity.value, "message": rule.description})

        # 2. Personal attributes (Policy 4.3)
        attribute_matches = self._checker.scan_patterns(ad_text)
        if attribute_matches:
            rule = RULES["META_PERSONAL_ATTRIBUTES_4_3"]
            for match in attribute_matches:
                violations.append(
                    {
                        "rule": rule.code,
                        "severity": rule.severity.value,
                        "message": f"{rule.description} Matched snippet: \"{match.snippet}\"",
                    }
                )

        # 3. Unverified claims
        claim_matches = self._checker.scan_phrases(ad_text)
        if claim_matches:
            rule = RULES["META_UNVERIFIED_CLAIMS"]
            warnings.append(
                {
                    "rule": rule.code,
                    "severity": rule.severity.value,
                    "message": f"{rule.description} Phrases found: {', '.join(claim_matches)}",
                }
            )

        # 4. Landing page / ad topic mismatch (simple keyword overlap heuristic)
        if landing_page_topic and ad_topic:
            lp_words = set(landing_page_topic.lower().split())
            ad_words = set(ad_topic.lower().split())
            if not (lp_words & ad_words):
                rule = RULES["META_LANDING_PAGE_MISMATCH"]
                warnings.append({"rule": rule.code, "severity": rule.severity.value, "message": rule.description})

        risk_score = max(0, 100 - (len(violations) * 35 + len(warnings) * 10))

        return {
            "passed": len(violations) == 0,
            "risk_score": risk_score,
            "violations": violations,
            "warnings": warnings,
        }
