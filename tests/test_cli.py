"""Tests for the Typer CLI. Previously this module had 0% coverage.

Commands that talk to Meta's APIs are exercised with respx mocks so
the test suite never touches the network.
"""

import httpx
import respx
from typer.testing import CliRunner

from meta_ecosystem_suite.cli import app

runner = CliRunner()


def test_lint_command_passes_clean_ad():
    result = runner.invoke(app, ["lint", "Great running shoes for everyday training."])
    assert result.exit_code == 0
    assert "complies" in result.stdout.lower()


def test_lint_command_flags_missing_ai_disclosure():
    result = runner.invoke(app, ["lint", "Some ad copy.", "--is-ai"])
    assert result.exit_code == 0
    assert "violation" in result.stdout.lower()


def test_metrics_normalize_command():
    result = runner.invoke(app, ["metrics", "normalize", "--impressions", "1000", "--reach", "500"])
    assert result.exit_code == 0
    assert '"total_views": 1000' in result.stdout
    assert '"unique_viewers": 500' in result.stdout


@respx.mock
def test_metrics_fetch_command():
    respx.get("https://graph.facebook.com/v19.0/999/insights").mock(
        return_value=httpx.Response(200, json={"data": [{"impressions": "10", "reach": "5"}]})
    )
    result = runner.invoke(app, ["metrics", "fetch", "999"])
    assert result.exit_code == 0
    assert '"total_views": 10' in result.stdout


@respx.mock
def test_sentinel_check_command(tmp_path):
    respx.get("https://graph.facebook.com").mock(return_value=httpx.Response(200))
    respx.get("https://graph.facebook.com/v19.0").mock(return_value=httpx.Response(200))
    respx.get("https://www.facebook.com/ads/library").mock(return_value=httpx.Response(200))
    result = runner.invoke(app, ["sentinel", "check", "--no-notify"])
    assert result.exit_code == 0
    assert "Meta Status Sentinel" in result.stdout


@respx.mock
def test_dsa_audit_command_writes_report(tmp_path):
    respx.get("https://graph.facebook.com/v19.0/ads_archive").mock(
        return_value=httpx.Response(200, json={"data": [], "paging": {}})
    )
    output_path = tmp_path / "report.json"
    result = runner.invoke(
        app,
        ["dsa", "audit", "shoes", "--limit", "5", "--output", str(output_path)],
    )
    assert result.exit_code == 0
    assert output_path.exists()


@respx.mock
def test_dsa_audit_command_supports_tiktok_platform(tmp_path):
    respx.post("https://open.tiktokapis.com/v2/research/adlib/ad/query/").mock(
        return_value=httpx.Response(200, json={"data": {"has_more": False, "ads": []}})
    )
    output_path = tmp_path / "report.json"
    result = runner.invoke(
        app,
        ["dsa", "audit", "coffee", "--platform", "tiktok", "--output", str(output_path)],
    )
    assert result.exit_code == 0
    assert "tiktok" in result.stdout.lower()
    assert output_path.exists()


def test_dsa_audit_command_rejects_unknown_platform(tmp_path):
    output_path = tmp_path / "report.json"
    result = runner.invoke(
        app,
        ["dsa", "audit", "coffee", "--platform", "google_ads", "--output", str(output_path)],
    )
    assert result.exit_code == 1
    assert "Unknown ad platform" in result.stdout
