from meta_ecosystem_suite.policy_linter.linter import AdPolicyLinter


def test_clean_ad_passes():
    linter = AdPolicyLinter()
    result = linter.lint_ad("Discover our new summer collection, now available online.")
    assert result["passed"] is True
    assert result["risk_score"] == 100


def test_missing_ai_disclosure_flagged():
    linter = AdPolicyLinter()
    result = linter.lint_ad("Check out this offer.", is_ai_generated=True, ai_disclosed=False)
    assert result["passed"] is False
    assert any(v["rule"] == "META_AI_DISCLOSURE_REQUIRED" for v in result["violations"])


def test_ai_disclosure_present_does_not_flag():
    linter = AdPolicyLinter()
    result = linter.lint_ad("Check out this offer.", is_ai_generated=True, ai_disclosed=True)
    assert not any(v["rule"] == "META_AI_DISCLOSURE_REQUIRED" for v in result["violations"])


def test_personal_attribute_violation():
    linter = AdPolicyLinter()
    result = linter.lint_ad("Are you struggling? We can help.")
    assert result["passed"] is False
    assert any(v["rule"] == "META_PERSONAL_ATTRIBUTES_4_3" for v in result["violations"])


def test_unverified_claims_warning():
    linter = AdPolicyLinter()
    result = linter.lint_ad("Our product offers 100% guaranteed results.")
    assert result["passed"] is True
    assert any(w["rule"] == "META_UNVERIFIED_CLAIMS" for w in result["warnings"])


def test_risk_score_decreases_with_violations():
    linter = AdPolicyLinter()
    clean = linter.lint_ad("A normal ad about shoes.")
    flagged = linter.lint_ad("Are you sick? Are you poor?")
    assert flagged["risk_score"] < clean["risk_score"]
