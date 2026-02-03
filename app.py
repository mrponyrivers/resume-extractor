import json
import os
import sys
import tempfile
from pathlib import Path

import streamlit as st

# --- Make imports work on Streamlit Cloud (and locally) ---
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from resume_tool.core import extract_resume  # noqa: E402
from resume_tool.cli import write_report_md  # noqa: E402


st.set_page_config(page_title="Resume Extractor (Local)", page_icon="📄", layout="wide")
st.title("📄 Resume Extractor (Local)")
st.caption("Upload a resume (PDF or TXT) → get structured JSON + a Markdown report. (Local parsing; no external LLM.)")

uploaded = st.file_uploader("Upload resume (.pdf or .txt)", type=["pdf", "txt"])

if not uploaded:
    st.info("Upload a PDF or TXT resume to begin.")
    st.stop()

# Save upload to a temp file so your existing extractor can read it
suffix = Path(uploaded.name).suffix.lower() or ".pdf"
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
    tmp.write(uploaded.getbuffer())
    in_path = Path(tmp.name)

try:
    with st.spinner("Extracting resume fields..."):
        data = extract_resume(str(in_path))

        out_dir = Path(tempfile.mkdtemp(prefix="resume_extract_"))
        json_path = out_dir / "resume.json"
        report_path = out_dir / "report.md"

        json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        write_report_md(str(report_path), data)

        report_md = report_path.read_text(encoding="utf-8")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("Extracted fields (JSON)")
        st.json(data)

        st.download_button(
            "Download resume.json",
            data=json.dumps(data, indent=2).encode("utf-8"),
            file_name="resume.json",
            mime="application/json",
        )

    with col2:
        st.subheader("Report (Markdown)")
        st.code(report_md, language="markdown")
        st.download_button(
            "Download report.md",
            data=report_md.encode("utf-8"),
            file_name="report.md",
            mime="text/markdown",
        )

    st.success("Done.")

finally:
    # Clean up the uploaded temp file
    try:
        in_path.unlink(missing_ok=True)
    except Exception:
        pass

