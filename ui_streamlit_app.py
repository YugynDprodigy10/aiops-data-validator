import streamlit as st
from pathlib import Path
from datetime import datetime

from valmods.xml_validator import XMLValidator
from valmods.json_validator import JSONValidator
from valmods.csv_validator import CSVValidator  # NEW: CSV support

from core.models import ValidationReport
from core.reasoner import enrich_with_suggestions, summarize
from core.reporter import to_markdown, to_html


# ---------- Page meta ----------
st.set_page_config(page_title="AI Ops Data Validator", page_icon="🛰️", layout="wide")
st.title("AI Ops Data Validator — No-code UI")
st.caption("Upload XML/JSON/CSV → Validate against schemas → Get a human-readable report.")


# ---------- Config panel ----------
with st.expander("⚙️ Configuration", expanded=False):
    kind = st.radio(
        "Standard",
        ["Auto-detect", "XML (PDS4)", "JSON"],
        index=0,
        horizontal=True
    )

    # XML (PDS4)
    xsd = st.text_input(
        "PDS4 root XSD",
        "schemas/minimal.xsd",
        help="Can be a local path or a remote URL (e.g., NASA PDS4 XSD)."
    )
    sch = st.text_input(
        "PDS4 Schematron (optional)",
        "",
        help="Optional .sch file for additional PDS4 rule checks."
    )

    # JSON
    json_schema = st.text_input(
        "JSON Schema",
        "schemas/sample.schema.json",
        help="Path to a JSON Schema file."
    )

    # CSV
    csv_schema = st.text_input(
        "CSV Schema (YAML)",
        "schemas/csv.schema.yaml",
        help="YAML file describing required columns, types, and simple rules."
    )


# ---------- Uploader ----------
uploads = st.file_uploader(
    "Drop files here",
    type=["xml", "json", "csv"],
    accept_multiple_files=True
)
run = st.button("▶️ Run validation", type="primary", use_container_width=True)


# ---------- Helpers ----------
def detect_kind(name: str) -> str:
    s = Path(name).suffix.lower()
    if s == ".xml":
        return "xml"
    if s == ".json":
        return "json"
    if s == ".csv":
        return "csv"
    return "unknown"


# ---------- Main run ----------
if run:
    if not uploads:
        st.warning("Please upload at least one file.")
        st.stop()

    run_dir = Path("ui_runs") / datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    results = []
    with st.spinner("Validating..."):
        for uf in uploads:
            # Save uploaded file to disk for validators
            path = run_dir / uf.name
            with open(path, "wb") as f:
                f.write(uf.getbuffer())

            # Decide which validator to use
            if kind == "Auto-detect":
                k = detect_kind(uf.name)
            else:
                k = "xml" if "XML" in kind else "json"

            # Run the appropriate validator
            if k == "xml":
                if not xsd:
                    st.error("Please provide a PDS4 XSD path/URL for XML validation.")
                    continue
                v = XMLValidator(xsd, sch or None)

            elif k == "json":
                if not json_schema:
                    st.error("Please provide a JSON Schema path for JSON validation.")
                    continue
                v = JSONValidator(json_schema)

            elif k == "csv":
                if not csv_schema:
                    st.error("Please provide a CSV Schema (YAML) path for CSV validation.")
                    continue
                v = CSVValidator(csv_schema)

            else:
                st.error(f"Unsupported file type for {uf.name}")
                continue

            # Validate and enrich with rule-based suggestions
            issues = v.validate(str(path))
            enrich_with_suggestions(issues)

            # Build report (counts/properties computed on the class)
            report = ValidationReport(file=str(path), issues=issues)
            results.append((path, report))

    # ---------- Summary tiles ----------
    total_files = len(results)
    total_errors = sum(r.error_count for _, r in results)
    total_warnings = sum(r.warning_count for _, r in results)

    c1, c2, c3 = st.columns(3)
    c1.metric("Files", total_files)
    c2.metric("Errors", total_errors)
    c3.metric("Warnings", total_warnings)

    # ---------- Per-file sections ----------
    for path, report in results:
        st.markdown(f"### {path.name} — {'✅ PASS' if report.passed else '❌ FAIL'}")
        st.markdown(to_markdown(report))

        # Provide HTML download
        html_bytes = to_html(report).encode("utf-8")
        st.download_button(
            "⬇️ Download HTML report",
            data=html_bytes,
            file_name=f"{path.stem}_report.html",
            mime="text/html",
            use_container_width=False,
        )
