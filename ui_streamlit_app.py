
import streamlit as st
from pathlib import Path
from datetime import datetime
import tempfile
import json

from valmods.xml_validator import XMLValidator
from valmods.json_validator import JSONValidator
from core.models import ValidationReport, ValidationIssue
from core.reasoner import enrich_with_suggestions, summarize
from core.reporter import to_markdown, to_html

st.set_page_config(page_title="AI Ops Data Validator", page_icon="🛰️", layout="wide")
st.title("AI Ops Data Validator — No‑code UI")
st.caption("Upload XML/JSON → Validate against schemas → Get a human‑readable report.")

with st.expander("⚙️ Configuration", expanded=False):
    kind = st.radio("Standard", ["Auto-detect", "XML (PDS4)", "JSON"], index=0, horizontal=True)
    xsd = st.text_input("PDS4 root XSD", "schemas/pds4/PDS4_PDS_1G00.xsd")
    sch = st.text_input("PDS4 Schematron (optional)", "")
    json_schema = st.text_input("JSON Schema", "schemas/json/dataset.schema.json")

uploads = st.file_uploader("Drop files here", type=["xml","json"], accept_multiple_files=True)
run = st.button("▶️ Run validation", type="primary", use_container_width=True)

def detect_kind(name: str) -> str:
    s = Path(name).suffix.lower()
    if s == ".xml": return "xml"
    if s == ".json": return "json"
    return "unknown"

if run:
    if not uploads:
        st.warning("Please upload at least one file.")
        st.stop()

    run_dir = Path("ui_runs") / datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    results = []
    with st.spinner("Validating..."):
        for uf in uploads:
            path = run_dir / uf.name
            with open(path, "wb") as f:
                f.write(uf.getbuffer())

            k = detect_kind(uf.name) if kind == "Auto-detect" else ("xml" if "XML" in kind else "json")
            if k == "xml":
                v = XMLValidator(xsd, sch or None)
            elif k == "json":
                v = JSONValidator(json_schema)
            else:
                st.error(f"Unsupported file type for {uf.name}")
                continue

            issues = v.validate(str(path))
            enrich_with_suggestions(issues)
            report = ValidationReport(
                file=str(path),
                passed=(len([i for i in issues if i.severity == "error"]) == 0),
                error_count=len([i for i in issues if i.severity == "error"]),
                warning_count=len([i for i in issues if i.severity == "warning"]),
                issues=issues
            )
            results.append((path, report))

    # Summary tiles
    total_files = len(results)
    total_errors = sum(r.error_count for _, r in results)
    total_warnings = sum(r.warning_count for _, r in results)
    c1,c2,c3 = st.columns(3)
    c1.metric("Files", total_files)
    c2.metric("Errors", total_errors)
    c3.metric("Warnings", total_warnings)

    # Per-file sections
    for path, report in results:
        st.markdown(f"### {path.name} — {'✅ PASS' if report.passed else '❌ FAIL'}")
        st.markdown(to_markdown(report))

        # Provide HTML download
        html = to_html(report).encode("utf-8")
        st.download_button(
            "⬇️ Download HTML report",
            data=html,
            file_name=f"{path.stem}_report.html",
            mime="text/html"
        )
