"""Unified command-line interface for MetaEcosystemSuite.

Exposes every module (DSA auditor, metrics migrator, policy linter,
status sentinel) behind a single `meta-suite` entrypoint.
"""

import asyncio
import json

import typer
from rich import print
from rich.panel import Panel
from rich.table import Table

from meta_ecosystem_suite.dsa_auditor.extractor import AdLibraryExtractor
from meta_ecosystem_suite.dsa_auditor.reporter import DSAReporter
from meta_ecosystem_suite.dsa_auditor.transformer import DSATransformer
from meta_ecosystem_suite.metrics_migrator.graph_client import GraphAPIClient
from meta_ecosystem_suite.metrics_migrator.normalizer import MetricsNormalizer
from meta_ecosystem_suite.policy_linter.linter import AdPolicyLinter
from meta_ecosystem_suite.status_sentinel.sentinel import MetaStatusSentinel

app = typer.Typer(
    name="meta-suite",
    help="Unified Developer & Compliance Engine for the Meta Graph API, Marketing API & EU DSA standards.",
    add_completion=False,
)

dsa_app = typer.Typer(help="EU DSA ad-transparency ETL commands.")
metrics_app = typer.Typer(help="Legacy -> unified metrics migration commands.")
sentinel_app = typer.Typer(help="API health & latency monitoring commands.")

app.add_typer(dsa_app, name="dsa")
app.add_typer(metrics_app, name="metrics")
app.add_typer(sentinel_app, name="sentinel")


@app.command()
def lint(
    text: str,
    is_ai: bool = typer.Option(False, "--is-ai", help="Mark this ad as AI-generated content."),
    ai_disclosed: bool = typer.Option(False, "--ai-disclosed", help="Mark AI disclosure label as present."),
) -> None:
    """Run the pre-launch Ad Policy & AI Disclosure linter on a single ad text."""
    linter = AdPolicyLinter()
    result = linter.lint_ad(text, is_ai_generated=is_ai, ai_disclosed=ai_disclosed)

    if result["passed"]:
        print(Panel(f"[bold green]Ad complies with Meta policies.[/bold green]\nRisk score: {result['risk_score']}/100", title="Ad Policy Linter"))
    else:
        print(Panel(f"[bold red]{len(result['violations'])} violation(s) detected.[/bold red]\nRisk score: {result['risk_score']}/100", title="Ad Policy Linter"))
        for v in result["violations"]:
            print(f"  • [bold red][{v['severity']}][/bold red] {v['message']}")
    for w in result["warnings"]:
        print(f"  • [bold yellow][{w['severity']}][/bold yellow] {w['message']}")


@metrics_app.command("normalize")
def normalize(
    impressions: int = typer.Option(..., "--impressions", help="Legacy impressions count."),
    reach: int = typer.Option(..., "--reach", help="Legacy reach count."),
) -> None:
    """Normalize raw impressions/reach into the unified Views/Viewers schema."""
    result = MetricsNormalizer.normalize_insights({"impressions": impressions, "reach": reach})
    print(json.dumps(result, indent=2))


@metrics_app.command("fetch")
def fetch_and_normalize(object_id: str) -> None:
    """Fetch live insights for a Graph API object and normalize them."""

    async def _run():
        client = GraphAPIClient()
        raw = await client.get_insights(object_id)
        return MetricsNormalizer.normalize_insights(raw)

    result = asyncio.run(_run())
    print(json.dumps(result, indent=2))


@dsa_app.command("audit")
def dsa_audit(
    search_terms: str,
    countries: str = typer.Option("EU", help="Comma-separated country codes."),
    limit: int = typer.Option(100, help="Max number of ad records to pull."),
    output: str = typer.Option("reports/dsa_report.json", help="Output path for the JSON report."),
) -> None:
    """Extract, transform, and report on ads matching `search_terms` per the EU DSA schema."""

    async def _run():
        extractor = AdLibraryExtractor()
        raw_ads = await extractor.fetch_ads(search_terms, ad_reached_countries=countries.split(","), limit=limit)
        records = DSATransformer.transform_batch(raw_ads)
        path = DSAReporter.write_json(records, output)
        return records, path

    records, path = asyncio.run(_run())
    print(Panel(f"Processed [bold]{len(records)}[/bold] ad record(s).\nReport written to: [bold]{path}[/bold]", title="DSA Auditor"))


@sentinel_app.command("check")
def sentinel_check(notify: bool = typer.Option(True, help="Send a Slack alert if issues are detected.")) -> None:
    """Run all registered API health probes once and print the results."""

    async def _run():
        sentinel = MetaStatusSentinel()
        return await sentinel.run_all(notify_on_issue=notify)

    results = asyncio.run(_run())

    table = Table(title="Meta Status Sentinel")
    table.add_column("Endpoint")
    table.add_column("Status")
    table.add_column("Latency (ms)")
    table.add_column("Detail")

    for r in results:
        color = {"HEALTHY": "green", "DEGRADED": "yellow", "OUTAGE": "red"}.get(r["status"], "white")
        table.add_row(r["name"], f"[{color}]{r['status']}[/{color}]", str(r["latency_ms"]), r["detail"])

    print(table)


if __name__ == "__main__":
    app()
