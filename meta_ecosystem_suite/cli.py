import typer
from rich import print
from rich.panel import Panel
from meta_ecosystem_suite.policy_linter.linter import AdPolicyLinter
from meta_ecosystem_suite.metrics_migrator.normalizer import MetricsNormalizer

app = typer.Typer(title="MetaEcosystemSuite Master CLI")

@app.command()
def lint(text: str, is_ai: bool = False, ai_disclosed: bool = False):
    """Linter pre-launch pentru reclame Meta Ads."""
    linter = AdPolicyLinter()
    res = linter.lint_ad(text, is_ai_generated=is_ai, ai_disclosed=ai_disclosed)
    
    if res["passed"]:
        print(Panel("[bold green]✓ Reclama respectă politicile Meta![/bold green]", title="Ad Policy Linter"))
    else:
        print(Panel(f"[bold red]✗ S-au detectat {len(res['violations'])} încălcări![/bold red]", title="Ad Policy Linter"))
        for v in res["violations"]:
            print(f" • [bold red][{v['severity']}][/bold red] {v['message']}")

@app.command()
def normalize(impressions: int, reach: int):
    """Normalizează metricile vechi în schema Views / Viewers."""
    res = MetricsNormalizer.normalize_insights({"impressions": impressions, "reach": reach})
    print(res)

if __name__ == "__main__":
    app()
