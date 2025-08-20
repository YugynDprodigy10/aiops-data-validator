# aiops_validator/core/reasoner.py
from collections import defaultdict
from core.models import ValidationIssue, Suggestion, ValidationReport

COMMON_PATTERNS = [
    # (predicate, suggestion builder)
    (
        lambda i: "Namespace" in i.message or "xmlns" in i.message,
        lambda i: Suggestion(
            message="Add the correct PDS4 namespace on the root element.",
            example='<Product_Observational xmlns="http://pds.nasa.gov/pds4/pds/v1">…</Product_Observational>'
        )
    ),
    (
        lambda i: "is not a valid value" in i.message and "unit" in i.message,
        lambda i: Suggestion(
            message="Replace with a valid unit from the PDS Units of Measure dictionary.",
            example='<value unit="K">120.3</value>'
        )
    ),
    (
        lambda i: "is a required property" in i.message or "Missing child element" in i.message,
        lambda i: Suggestion(
            message="Add the required field/element according to the schema.",
            example='… "title": "Mars image 123" …'
        )
    ),
]

def enrich_with_suggestions(issues: list[ValidationIssue]) -> None:
    for i in issues:
        for pred, build in COMMON_PATTERNS:
            if pred(i) and i.suggestion is None:
                i.suggestion = build(i)
                break

def summarize(report: ValidationReport) -> str:
    # Group by high-level cause for a human-friendly paragraph
    buckets = defaultdict(list)
    for i in report.issues:
        key = ("namespace" if (i.suggestion and "namespace" in i.suggestion.message.lower())
               else "required" if "required" in i.message.lower()
               else "type" if "type" in i.message.lower()
               else i.issue_type)
        buckets[key].append(i)
    parts = [f"{report.file}: {report.error_count} error(s), {report.warning_count} warning(s)."]
    for k, vals in buckets.items():
        sample = vals[0]
        parts.append(f"- {k}: {len(vals)} issue(s). Example @ {sample.path}: {sample.message}")
    return "\n".join(parts)

