from pathlib import Path
from urllib.parse import urlparse
from typing import List, Optional
from xmlschema import XMLSchema
from lxml import etree
from lxml.isoschematron import Schematron
from core.models import ValidationIssue

# NEW: tiny cache helper (no extra deps)
import hashlib, os, tempfile, urllib.request

def _cache_fetch(url: str, suffix: str) -> str:
    """
    Download URL once into a temp cache and return the local filepath.
    Reuses cached file on subsequent runs.
    """
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16] + suffix
    cache_dir = os.path.join(tempfile.gettempdir(), "aiops_xsd_cache")
    os.makedirs(cache_dir, exist_ok=True)
    dest = os.path.join(cache_dir, h)
    if not os.path.exists(dest):
        with urllib.request.urlopen(url, timeout=30) as r, open(dest, "wb") as f:
            f.write(r.read())
    return dest


class XMLValidator:
    standard = "PDS4-XML"

    def __init__(self, xsd_path: str, schematron_path: Optional[str] = None):
        # XSD: accept local path or http(s) URL (cache URLs)
        x_parsed = urlparse(xsd_path) if xsd_path else None
        if x_parsed and x_parsed.scheme in ("http", "https"):
            xsd_local = _cache_fetch(xsd_path, ".xsd")
        else:
            xsd_local = str(Path(xsd_path))

        self.schema = XMLSchema(xsd_local)

        # Schematron (optional): also allow URL + cache
        self.schematron = None
        if schematron_path:
            s_parsed = urlparse(schematron_path)
            sch_local = (
                _cache_fetch(schematron_path, ".sch")
                if s_parsed and s_parsed.scheme in ("http", "https")
                else str(Path(schematron_path))
            )
            sch_doc = etree.parse(sch_local)
            self.schematron = Schematron(sch_doc)

    def validate(self, path: str) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        # Parse once so we can reuse for Schematron and get useful error locations
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
