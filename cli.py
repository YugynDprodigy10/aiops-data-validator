# aiops_validator/cli.py
import json, sys
import typer
from validators.xml_validator import XMLValidator
from validators.json_validator import JSONValidator
from core.models import ValidationReport
from core.reasoner import enrich_with_suggestions, summarize
from core.reporter import to_markdown

app = typer.Typer()

@app.command()
def validate(
    file: str,
    kind: str = typer.Option(..., help="xml|json"),
    xsd: str = typer.Option(None),
    schematron: str = typer.Option(None),
    json_schema: str = typer.Option(None),
    out: str = typer.Option(None, help="Write Markdown report to this file")
):
    if kind == "xml":
        v = XMLValidator(xsd_path=xsd, schematron_path=schematron)
        issues = v.validate(file)
    elif kind == "json":
        v = JSONValidator(schema_path=json_schema)
        issues = v.validate(file)
    else:
        typer.echo("Unsupported kind", err=True); raise typer.Exit(code=2)

    errors = sum(1 for i in issues if i.severity == "error")
    warnings = sum(1 for i in issues if i.severity == "warning")
    report = ValidationReport(
        file=file, passed=(errors == 0), error_count=errors, warning_count=warnings, issues=issues
    )

    enrich_with_suggestions(report.issues)
    text = summarize(report)

    md = to_markdown(report)
    if out:
        with open(out, "w", encoding="utf-8") as f: f.write(md)
        typer.echo(f"Wrote {out}")
    else:
        typer.echo(md)

    raise typer.Exit(code=0 if report.passed else 2)

if __name__ == "__main__":
    app()

