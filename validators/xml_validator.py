
from .base import BaseValidator
from core.models import ValidationIssue
from lxml import etree
import xmlschema
import uuid
from core.models import ValidationIssue

class XMLValidator(BaseValidator):
    def __init__(self, xsd_path: str, schematron_path: str | None = None):
        self.schema = xmlschema.XMLSchema(xsd_path)            # compile once
        self.schematron = None
        if schematron_path:
            sch_doc = etree.parse(schematron_path)
            self.schematron = etree.Schematron(sch_doc)

    def validate(self, file_path: str) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        # 1) Well-formedness
        try:
            tree = etree.parse(file_path)
        except etree.XMLSyntaxError as e:
            issues.append(ValidationIssue(
                id=str(uuid.uuid4()),
                issue_type="wellformedness",
                severity="error",
                path="/",
                line=getattr(e, "position", (None, None))[0],
                column=getattr(e, "position", (None, None))[1],
                message=str(e)
            ))
            return issues

        # 2) XSD
        for err in self.schema.iter_errors(file_path):
            line, col = getattr(err, "position", (None, None))
            issues.append(ValidationIssue(
                id=str(uuid.uuid4()),
                issue_type="schema",
                severity="error",
                path=str(getattr(err, "path", "")),        # XPath-like
                line=line, column=col,
                rule=getattr(err, "schema_path", None),
                message=str(err)
            ))

        # 3) Schematron (optional but important for PDS4)
        if self.schematron:
            is_ok = self.schematron.validate(tree)
            if not is_ok:
                for log in self.schematron.error_log:
                    issues.append(ValidationIssue(
                        id=str(uuid.uuid4()),
                        issue_type="schematron",
                        severity="error",
                        path="/", # Schematron logs vary; enrich in reasoner
                        line=log.line, column=log.column,
                        rule=getattr(log, "type_name", None),
                        message=log.message
                    ))
        return issues


