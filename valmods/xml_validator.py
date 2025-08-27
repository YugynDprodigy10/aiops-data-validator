# valmods/xml_validator.py
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Optional
from xmlschema import XMLSchema
from lxml import etree
from lxml.isoschematron import Schematron
from core.models import ValidationIssue

class XMLValidator:
    standard = "PDS4-XML"

    def __init__(self, xsd_path: str, schematron_path: Optional[str] = None):
        parsed = urlparse(xsd_path)
        xsd_source = xsd_path if parsed.scheme in ("http", "https") else str(Path(xsd_path))
        self.schema = XMLSchema(xsd_source)

        self.schematron = None
        if schematron_path:
            sch_doc = etree.parse(str(schematron_path))
            self.schematron = Schematron(sch_doc)

    def validate(self, path: str) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        # Parse once so we can reuse for Schematron and line/col as needed
        try:
            doc = etree.parse(str(path))
        except Exception as e:
            return [ValidationIssue(issue_type="XML-PARSE", severity="error", path="$", message=str(e))]

        # XSD
        for err in self.schema.iter_errors(str(path)):
            issues.append(
                ValidationIssue(
                    issue_type="XSD-VALIDATION",
                    severity="error",
                    path=str(err.path) or "(unknown)",
                    message=str(err),
                )
            )

        # Schematron (if provided)
        if self.schematron and not self.schematron.validate(doc):
            for e in self.schematron.error_log:
                issues.append(
                    ValidationIssue(
                        issue_type="SCHEMATRON",
                        severity="error",
                        path=e.path or "(unknown)",
                        message=e.message,
                    )
                )
        return issues
