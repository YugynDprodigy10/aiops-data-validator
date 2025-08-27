
from pathlib import Path
def detect_kind(p: Path) -> str:
    ext = p.suffix.lower()
    if ext == ".xml": return "xml"
    if ext == ".json": return "json"
    if ext == ".csv": return "csv"
    return "unknown"
