import pytest
from meta_ecosystem_suite.policy_linter.linter import AdPolicyLinter

def test_ai_disclosure_violation():
    linter = AdPolicyLinter()
    result = linter.lint_ad("This is an AI generated ad.", is_ai_generated=True, ai_disclosed=False)
    assert not result["passed"]
    assert any(v["rule"] == "META_AI_DISCLOSURE_REQUIRED" for v in result["violations"])

def test_personal_attributes_violation():
    linter = AdPolicyLinter()
    result = linter.lint_ad("Ești depresiv? Cumpără acum!", is_ai_generated=False, ai_disclosed=True)
    assert not result["passed"]
    assert any(v["rule"] == "META_PERSONAL_ATTRIBUTES_4_3" for v in result["violations"])

def test_unverified_claims_warning():
    linter = AdPolicyLinter()
    result = linter.lint_ad("Acest produs este 100% garantat să funcționeze.", is_ai_generated=False, ai_disclosed=True)
    assert result["passed"]
    assert any(w["rule"] == "META_UNVERIFIED_CLAIMS" for w in result["warnings"])

def test_clean_ad():
    linter = AdPolicyLinter()
    result = linter.lint_ad("Descoperă noul nostru produs inovator!", is_ai_generated=False, ai_disclosed=True)
    assert result["passed"]
    assert len(result["violations"]) == 0
    assert len(result["warnings"]) == 0
