
from dataclasses import dataclass, field
from typing import List, Optional, Literal, Dict, Any

Severity = Literal["error", "warning", "info"]
IssueType = Literal["schema", "schematron", "wellformedness", "conformance"]

@dataclass
class Suggestion:
    message: str
    patch: Optional[Dict[str, Any]] = None   # JSON Patch ops or XML edit hint
    example: Optional[str] = None            # tiny snippet showing the fix

@dataclass
class ValidationIssue:
    id: str
    issue_type: IssueType
    severity: Severity
    path: str                 # XPath or JSON Pointer
    line: Optional[int] = None
    column: Optional[int] = None
    rule: Optional[str] = None # schema path / schematron rule id
    message: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    suggestion: Optional[Suggestion] = None

@dataclass
class ValidationReport:
    file: str
    passed: bool
    error_count: int
    warning_count: int
    issues: List[ValidationIssue] = field(default_factory=list)

