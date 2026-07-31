import re
from typing import Any, Dict, List


class AdPolicyLinter:
    """
    Pre-flight linter for validating advertisements against
    Meta Advertising Policies before publication.
    """

    # Meta Advertising Policy 4.3 - Personal Attributes
    SENSITIVE_PATTERNS = [
        r"\byou\b.*\b(depressed|sick|ill|in debt|lonely|poor)\b",
        r"\bare you\b.*\b(depressed|sick|ill|in debt|lonely|poor)\b",
        r"\besti\b.*\b(depresiv|bolnav|indatorat|singur|sarac)\b",
        r"\bești\b.*\b(depresiv|bolnav|îndatorat|singur|sărac)\b",
        r"\bdo you suffer from\b",
        r"\bsuferi de\b",
        r"\bare you looking for treatment\b",
        r"\bcauți un tratament pentru\b",
    ]

    def lint_ad(
        self,
        ad_text: str,
        is_ai_generated: bool = False,
        ai_disclosed: bool = False,
    ) -> Dict[str, Any]:
        """
        Validate advertisement text against a subset of Meta Ads policies.

        Returns
        -------
        passed : bool
            True if no blocking policy violations were found.

        risk_score : int
            Simple heuristic score (0-100).

        violations : list
            Blocking policy violations.

        warnings : list
            Non-blocking recommendations.
        """

        violations: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []

        normalized_text = ad_text.lower()

        # ------------------------------------------------------------------
        # Meta AI Disclosure
        # ------------------------------------------------------------------
        if is_ai_generated and not ai_disclosed:
            violations.append(
                {
                    "rule": "META_AI_DISCLOSURE_REQUIRED",
                    "severity": "HIGH",
                    "message": (
                        "This advertisement contains AI-generated content "
                        "without the required Meta AI disclosure."
                    ),
                }
            )

        # ------------------------------------------------------------------
        # Meta Policy 4.3 - Personal Attributes
        # ------------------------------------------------------------------
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, normalized_text, re.IGNORECASE):
                violations.append(
                    {
                        "rule": "META_PERSONAL_ATTRIBUTES_4_3",
                        "severity": "CRITICAL",
                        "message": (
                            "The advertisement directly references sensitive "
                            "personal attributes."
                        ),
                    }
                )
                break

        # ------------------------------------------------------------------
        # Unverified Claims
        # ------------------------------------------------------------------
        if "100% guaranteed" in normalized_text or "100% garantat" in normalized_text:
            warnings.append(
                {
                    "rule": "META_UNVERIFIED_CLAIMS",
                    "severity": "MEDIUM",
                    "message": (
                        "Claims such as '100% guaranteed' may increase the "
                        "likelihood of automated review or delivery limitations."
                    ),
                }
            )

        risk_score = max(
            0,
            100 - (len(violations) * 35 + len(warnings) * 10),
        )

        return {
            "passed": len(violations) == 0,
            "risk_score": risk_score,
            "violations": violations,
            "warnings": warnings,
        }