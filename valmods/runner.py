# valmods/runner.py
from pathlib import Path
from typing import List, Tuple
from valmods.detector import detect_kind
from valmods.xml_validator import XMLValidator
from valmods.json_validator import JSONValidator
try:
    from valmods.csv_validator import CSVValidator
except Exception:
    CSVValidator = None
from core.models import ValidationReport

def run_validation(
    target: str, *, xsd_path: str | None, json_schema_path: str | None,
    csv_schema_path: str | None = None, schematron_path: str | None = None  # NEW
) -> List[Tuple[Path, ValidationReport]]:
    root = Path(target)
    files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
    xml_v = XMLValidator(xsd_path, schematron_path=schematron_path) if xsd_path else None  # CHANGED
    json_v = JSONValidator(json_schema_path) if json_schema_path else None
    csv_v = CSVValidator(csv_schema_path) if (csv_schema_path and CSVValidator) else None

    results = []
    for p in files:
        kind = detect_kind(p)
        if kind == "xml" and xml_v:
            issues = xml_v.validate(str(p))
        elif kind == "json" and json_v:
            issues = json_v.validate(str(p))
        elif kind == "csv" and csv_v:
            issues = csv_v.validate(str(p))
        else:
            continue
        results.append((p, ValidationReport(file=str(p), issues=issues)))
    return results
