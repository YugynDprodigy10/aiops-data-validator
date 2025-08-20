
from .base import BaseValidator
from aiops_validator.core.models import ValidationIssue
from jsonschema import Draft202012Validator
import json, uuid

def to_json_pointer(path_deque) -> str:
    parts = []
    for p in list(path_deque):
        p = str(p).replace("~", "~0").replace("/", "~1")
        parts.append(p)
    return "/" + "/".join(parts)

class JSONValidator(BaseValidator):
    def __init__(self, schema_path: str):
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        self.validator = Draft202012Validator(self.schema)

    def validate(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            instance = json.load(f)

        issues = []
        for err in self.validator.iter_errors(instance):
            issues.append(ValidationIssue(
                id=str(uuid.uuid4()),
                issue_type="schema",
                severity="error",
                path=to_json_pointer(err.path),
                rule="/".join(map(str, err.schema_path)),
                message=err.message
            ))
        return issues
