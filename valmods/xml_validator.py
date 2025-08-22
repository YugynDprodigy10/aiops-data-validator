# valmods/xml_validator.py
from pathlib import Path
from urllib.parse import urlparse
from typing import List
import hashlib

from xmlschema import XMLSchema, XMLSchemaValidationError
from core.models import ValidationIssue


def _make_issue_id(code: str, loc: str, msg: str) -> str:
    """Deterministic short ID for an issue (good for dedup/diff)."""
    h = hashlib.sha1(f"{code}|{loc}|{msg}".encode("utf-8")).hexdigest()
    return h[:8]


class XMLValidator:
    standard = "PDS4-XML"

    def __init__(self, xsd_path: str, schematron_path: str = None):
        # Accept http(s) URLs or local paths
        parsed = urlparse(xsd_path)
        if parsed.scheme in ("http", "https"):
            xsd_uri = xsd_path
        else:
            p = Path(xsd_path).expanduser().resolve()
            if not p.is_file():
                raise FileNotFoundError(f"PDS4 XSD not found at: {p}")
            xsd_uri = p.as_uri()

        self.schema = XMLSchema(xsd_uri)
        self.schematron_path = schematron_path  # reserved for future use

    def validate(self, path: str) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        try:
            self.schema.validate(path)
        except XMLSchemaValidationError:
            for err in self.schema.iter_errors(path):
                code = "XSD-VALIDATION"
                loc = str(err.path) or "(unknown)"
                msg = str(err)
                issues.append(
                    ValidationIssue(
                        id=_make_issue_id(code, loc, msg),
                        issue_type=code,
                        severity="error",
                        path=loc,
                        message=msg,
                        suggestion=None,
                    )
                )
        return issues
