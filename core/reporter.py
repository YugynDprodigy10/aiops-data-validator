# aiops_validator/core/reporter.py
from jinja2 import Environment, FileSystemLoader
from core.models import ValidationReport


env = Environment(loader=FileSystemLoader("templates"), autoescape=True)

def to_markdown(report: ValidationReport) -> str:
    tpl = env.get_template("report.md.j2")
    return tpl.render(report=report)

def to_html(report: ValidationReport) -> str:
    tpl = env.get_template("report.html.j2")
    return tpl.render(report=report)

