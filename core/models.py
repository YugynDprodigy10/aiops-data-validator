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
    issue_type: str
    severity: str
    path: str
    message: str
    rule: Optional[str] = None
    suggestion: Optional[Suggestion] = None
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

    @property
    def passed(self) -> bool:
        # ✅ add this
        return self.error_count == 0
