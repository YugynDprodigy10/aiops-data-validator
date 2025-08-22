from pathlib import Path
from urllib.parse import urlparse
from typing import List
from xmlschema import XMLSchema, XMLSchemaValidationError
from core.models import ValidationIssue

class XMLValidator:
    standard = "PDS4-XML"

    def __init__(self, xsd_path: str, schematron_path: str = None):
        parsed = urlparse(xsd_path)
        if parsed.scheme in ("http", "https"):
            xsd_uri = xsd_path
        else:
            p = Path(xsd_path).expanduser().resolve()
            if not p.is_file():
                raise FileNotFoundError(f"PDS4 XSD not found at: {p}")
            xsd_uri = p.as_uri()
        self.schema = XMLSchema(xsd_uri)
        self.schematron_path = schematron_path  # reserved for later

    def validate(self, path: str) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        try:
            self.schema.validate(path)
        except XMLSchemaValidationError:
            for err in self.schema.iter_errors(path):
                issues.append(
                    ValidationIssue(
                        issue_type="XSD-VALIDATION",
                        severity="error",
                        path=str(err.path) or "(unknown)",
                        message=str(err),
                        suggestion=None,
                    )
                )
        return issues
