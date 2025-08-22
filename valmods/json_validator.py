from typing import List
import json
from jsonschema import Draft202012Validator
from core.models import ValidationIssue

class JSONValidator:
    standard = "JSON"

    def __init__(self, schema_path: str):
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        self.validator = Draft202012Validator(self.schema)

    def validate(self, path: str) -> List[ValidationIssue]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        issues: List[ValidationIssue] = []
        for err in self.validator.iter_errors(data):
            issues.append(
                ValidationIssue(
                    issue_type="JSON-SCHEMA",
                    severity="error",
                    path=".".join(map(str, err.path)) or "$",
                    message=err.message,
                    suggestion=None,
                )
            )
        return issues
