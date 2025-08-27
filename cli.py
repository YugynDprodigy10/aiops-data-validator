# aiops-data-validator/cli.py
from __future__ import annotations

from pathlib import Path
import typer

from valmods.runner import run_validation
from core.reporter import to_markdown, to_html
from core.reasoner import enrich_with_suggestions, summarize


def main(
    path: str = typer.Argument(..., help="File or directory to validate"),
    xsd: str = typer.Option(None, "--xsd", help="XML XSD path or URL (for .xml files)"),
    sch: str = typer.Option(None, "--sch", help="Schematron .sch file for XML (optional)"),
    json_schema: str = typer.Option(None, "--json-schema", help="JSON Schema path (for .json files)"),
    csv_schema: str = typer.Option(None, "--csv-schema", help="CSV schema YAML path (for .csv files)"),
    out: str = typer.Option(None, "--out", help="Directory to write per-file reports (MD, and HTML if --html)"),
    html: bool = typer.Option(False, "--html", help="Also write per-file HTML reports when --out is set"),
    use_rules: bool = typer.Option(True, "--rules/--no-rules", help="Attach rule-based suggestions to issues"),
) -> None:

    target = Path(path)
    if not target.exists():
        typer.secho(f"[ERROR] Path not found: {target}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    # Run validations (auto-detect by file extension)
    results = run_validation(
        target=str(target),
        xsd_path=xsd,
        json_schema_path=json_schema,
        csv_schema_path=csv_schema,
        schematron_path=sch,  # <- optional Schematron support
    )

    if not results:
        typer.secho("No supported files found (xml/json/csv).", fg=typer.colors.YELLOW)
        raise typer.Exit(code=0)

    out_dir: Path | None = None
    if out:
        out_dir = Path(out)
        out_dir.mkdir(parents=True, exist_ok=True)

    any_errors = False
    summaries: list[str] = []

    for _, report in results:
        if use_rules:
            enrich_with_suggestions(report.issues)  # mutates in-place

        any_errors |= (report.error_count > 0)
        summaries.append(summarize(report))

        md = to_markdown(report)

        if out_dir:
            (out_dir / f"{Path(report.file).stem}_report.md").write_text(md, encoding="utf-8")
            if html:
                (out_dir / f"{Path(report.file).stem}_report.html").write_text(to_html(report), encoding="utf-8")
        else:
            typer.echo(md)
            typer.echo("\n---\n")

    if out_dir:
        (out_dir / "summary.md").write_text("\n".join(summaries) + "\n", encoding="utf-8")
        typer.secho(f"Wrote reports to {out_dir}", fg=typer.colors.GREEN)

    # Exit 0 if all passed; 2 if any errors
    raise typer.Exit(code=0 if not any_errors else 2)


if __name__ == "__main__":
    typer.run(main)
