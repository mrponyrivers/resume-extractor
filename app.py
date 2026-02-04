import json
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


SAMPLE_PATH = ROOT / "sample_resume.txt"

# --- Input: sample button OR uploader ---
colA, colB = st.columns([1, 2])
with colA:
    use_sample = st.button("📄 Use sample_resume.txt", use_container_width=True)
with colB:
    uploaded = st.file_uploader("Upload resume (.pdf or .txt)", type=["pdf", "txt"])

# Decide input file path
temp_file_path = None  # track temp upload so we only delete temp files

if use_sample:
    if not SAMPLE_PATH.exists():
        st.error("sample_resume.txt not found in the repo root.")
        st.stop()
    in_path = SAMPLE_PATH
else:
    if not uploaded:
        st.info("Upload a PDF/TXT resume, or click **📄 Use sample_resume.txt**.")
        st.stop()

    # Save upload to a temp file so your existing extractor can read it
    suffix = Path(uploaded.name).suffix.lower() or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getbuffer())
        temp_file_path = tmp.name

    in_path = Path(temp_file_path)

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
            use_container_width=True,
        )

    with col2:
        st.subheader("Report (Markdown)")
        st.code(report_md, language="markdown")
        st.download_button(
            "Download report.md",
            data=report_md.encode("utf-8"),
            file_name="report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.success("Done.")

finally:
    # Clean up ONLY the uploaded temp file (never delete sample_resume.txt)
    if temp_file_path:
        try:
            Path(temp_file_path).unlink(missing_ok=True)
        except Exception:
            pass
