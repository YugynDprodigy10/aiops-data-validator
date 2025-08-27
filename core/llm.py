
import os
from core.models import ValidationIssue, Suggestion
def enrich_with_llm(issues):
    if not os.getenv("USE_LLM"):  # gate by env
        return []
    out = []
    for i in issues:
        out.append(Suggestion(message=f"AI hint for {i.issue_type}: check {i.path} — {i.message[:80]}…"))
    return out
