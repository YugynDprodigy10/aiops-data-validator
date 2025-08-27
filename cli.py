# aiops-data-validator/cli.py
from __future__ import annotations

from pathlib import Path
import typer

from valmods.runner import run_validation
from core.reporter import to_markdown, to_html
from core.reasoner import enrich_with_suggestions, summarize


def main(
    path: str = typer.Argument(..., help="File or directory to validate"),
    xsd: str = typer.Option(None, "--xsd", help="Path to XML XSD (for .xml files)"),
    json_schema: str = typer.Option(None, "--json-schema", help="Path to JSON Schema (for .json files)"),
    csv_schema: str = typer.Option(None, "--csv-schema", help="Path to CSV schema YAML (for .csv files)"),
    out: str = typer.Option(None, "--out", help="Output directory for reports"),
    html: bool = typer.Option(False, "--html", help="Also write per-file HTML reports"),
    use_rules: bool = typer.Option(True, "--rules/--no-rules", help="Attach rule-based suggestions"),
):
    """
    Validate XML/JSON/CSV files against schemas.

    Example:
      python cli.py examples/ --xsd schemas/minimal.xsd --json-schema schemas/sample.schema.json --out out --html
    """
    target = Path(path)
    if not target.exists():
        typer.secho(f"[ERROR] Path not found: {target}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    results = run_validation(
        target=str(target),
        xsd_path=xsd,
        json_schema_path=json_schema,
        csv_schema_path=csv_schema,
    )

    if not results:
        typer.secho("No supported files found.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=0)

    any_errors = False
    out_dir = Path(out) if out else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    for _, report in results:
        if use_rules:
            enrich_with_suggestions(report.issues)

        any_errors |= report.error_count > 0
        md = to_markdown(report)

        if out_dir:
            (out_dir / f"{Path(report.file).stem}_report.md").write_text(md, encoding="utf-8")
            if html:
                (out_dir / f"{Path(report.file).stem}_report.html").write_text(to_html(report), encoding="utf-8")
        else:
            typer.echo(md)
            typer.echo("\n---\n")

    raise typer.Exit(code=0 if not any_errors else 2)


if __name__ == "__main__":
    typer.run(main)
