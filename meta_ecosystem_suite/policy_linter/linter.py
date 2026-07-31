import re
from typing import Dict, List, Any

class AdPolicyLinter:
    """Linter pre-launch pentru verificarea reclamelor conform regulilor Meta Ads."""

    SENSITIVE_PATTERNS = [
        r"ești și tu (depresiv|bolnav|îndatorat)\\?",
        r"cauți un tratament pentru",
        r"suferi de",
        r"ești (sărac|singur)\\?"
    ]

    def lint_ad(
        self, 
        ad_text: str, 
        is_ai_generated: bool = False, 
        ai_disclosed: bool = False
    ) -> Dict[str, Any]:
        violations = []
        warnings = []

        # 1. Regula de declarare a conținutului AI (Meta AI Disclosure)
        if is_ai_generated and not ai_disclosed:
            violations.append({
                "rule": "META_AI_DISCLOSURE_REQUIRED",
                "severity": "HIGH",
                "message": "Reclama folosește conținut AI fără eticheta obligatorie de transparență Meta."
            })

        # 2. Regula Atributelor Personale (Meta Policy 4.3)
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, ad_text, re.IGNORECASE):
                violations.append({
                    "rule": "META_PERSONAL_ATTRIBUTES_4_3",
                    "severity": "CRITICAL",
                    "message": f"Textul conține referiri directe la atribute personale sensibile."
                })

        # 3. Verificare promisiuni exagerate
        if "100% garantat" in ad_text.lower():
            warnings.append({
                "rule": "META_UNVERIFIED_CLAIMS",
                "severity": "MEDIUM",
                "message": "Formulările de tip '100% garantat' pot declanșa limitarea automată a contului."
            })

        risk_score = max(0, 100 - (len(violations) * 35 + len(warnings) * 10))

        return {
            "passed": len(violations) == 0,
            "risk_score": risk_score,
            "violations": violations,
            "warnings": warnings
        }
