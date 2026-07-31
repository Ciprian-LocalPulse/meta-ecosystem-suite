import pytest

from meta_ecosystem_suite.policy_linter.linter import AdPolicyLinter


def test_ai_disclosure_required():
    linter = AdPolicyLinter()

    result = linter.lint_ad(
        ad_text="AI generated advertisement",
        is_ai_generated=True,
        ai_disclosed=False,
    )

    assert not result["passed"]

    assert any(
        violation["rule"] == "META_AI_DISCLOSURE_REQUIRED"
        for violation in result["violations"]
    )


def test_personal_attributes_violation():
    linter = AdPolicyLinter()

    result = linter.lint_ad(
        ad_text="Are you depressed? Buy now!",
        is_ai_generated=False,
        ai_disclosed=True,
    )

    assert not result["passed"]

    assert any(
        violation["rule"] == "META_PERSONAL_ATTRIBUTES_4_3"
        for violation in result["violations"]
    )


def test_valid_ad():
    linter = AdPolicyLinter()

    result = linter.lint_ad(
        ad_text="Discover our new productivity application.",
        is_ai_generated=False,
        ai_disclosed=True,
    )

    assert result["passed"]
    assert result["risk_score"] == 100