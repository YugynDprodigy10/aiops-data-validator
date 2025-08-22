# core/models.py
from dataclasses import dataclass, field
from typing import Optional, List
from uuid import uuid4

@dataclass
class Suggestion:
    message: str
    example: Optional[str] = None

@dataclass
class ValidationIssue:
    # non-default fields first
    issue_type: str           # e.g., "XSD-VALIDATION", "JSON-SCHEMA"
    severity: str             # "error" | "warning" | "info"
    path: str                 # xpath/jsonpath/row:col
    message: str
    suggestion: Optional[str] = None
    # default field last
    id: str = field(default_factory=lambda: uuid4().hex[:8])

@dataclass
class ValidationReport:
    file: str
    issues: List[ValidationIssue]

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")
