from typing import List
from pathlib import Path
import pandas as pd, yaml
from core.models import ValidationIssue

class CSVValidator:
    standard = "CSV"

    def __init__(self, schema_yaml: str):
        spec = yaml.safe_load(Path(schema_yaml).read_text())
        self.required = spec.get("required_columns", [])
        self.types = spec.get("types", {})
        self.rules = spec.get("rules", [])

    def validate(self, path: str) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        try:
            df = pd.read_csv(path)
        except Exception as e:
            return [ValidationIssue("CSV-PARSE", "error", path="$", message=str(e))]
        # required
        for col in self.required:
            if col not in df.columns:
                issues.append(ValidationIssue("CSV-MISSING-COLUMN", "error", path="$", message=f"Missing column: {col}"))
        # types
        for col, t in self.types.items():
            if col not in df.columns:
                continue
            s = df[col].dropna()
            ok = (t=="int" and pd.api.types.is_integer_dtype(s)) or \
                 (t=="float" and (pd.api.types.is_float_dtype(s) or pd.api.types.is_integer_dtype(s))) or \
                 (t=="str" and s.astype(str).dtype == object)
            if not ok:
                issues.append(ValidationIssue("CSV-TYPE", "error", path=f"$.{col}", message=f"{col} expected {t}"))
        # simple rules
        for r in self.rules:
            kind, col = r.get("kind"), r.get("column")
            if col not in df.columns: continue
            if kind == "nonempty" and df[col].isna().any():
                issues.append(ValidationIssue("CSV-RULE-NONEMPTY", "error", f"$.{col}", f"Empty values in {col}"))
            if kind == "min" and (df[col] < r["value"]).any():
                issues.append(ValidationIssue("CSV-RULE-MIN", "error", f"$.{col}", f"{col} below {r['value']}"))
            if kind == "max" and (df[col] > r["value"]).any():
                issues.append(ValidationIssue("CSV-RULE-MAX", "error", f"$.{col}", f"{col} above {r['value']}"))
        return issues
