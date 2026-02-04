# Resume Extractor (Local)
## Live demo
<https://mrponyrivers-resume-extractor.streamlit.app/>

Local-only resume parser that extracts basic fields from a resume PDF/TXT into:
- resume.json
- report.md

Setup
- python3 -m venv .venv
- source .venv/bin/activate
- python -m pip install --upgrade pip
- pip install pypdf

Run
- PYTHONPATH=src python3 -m resume_tool.cli --input sample_resume.txt --json resume.json --report report.md
