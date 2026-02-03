import json
import tempfile
from pathlib import Path

import gradio as gr

from resume_tool.core import extract_resume
from resume_tool.cli import write_report_md


def run_extraction(uploaded_file):
    if uploaded_file is None:
        return "Please upload a PDF or TXT resume.", None, None

    # Gradio gives us a temp file path
    in_path = Path(uploaded_file)

    # Run extraction (your existing core logic)
    data = extract_resume(str(in_path))

    # Write outputs to temp files so Gradio can return downloadable files
    out_dir = Path(tempfile.mkdtemp(prefix="resume_extract_"))

    json_path = out_dir / "resume.json"
    report_path = out_dir / "report.md"

    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    write_report_md(str(report_path), data)

    summary = (
        f"Name guess: {data.get('name_guess','')}\n"
        f"Emails: {', '.join(data.get('contacts', {}).get('emails', []))}\n"
        f"Phones: {', '.join(data.get('contacts', {}).get('phones', []))}\n"
        f"Skills found: {', '.join(data.get('skills_found', []))}\n"
    )

    return summary, str(json_path), str(report_path)


with gr.Blocks() as demo:
    gr.Markdown("# Resume Extractor (Local)\nUpload a resume (PDF or TXT) and get structured JSON + a report.")
    file_in = gr.File(label="Upload resume (.pdf or .txt)", file_types=[".pdf", ".txt"])
    run_btn = gr.Button("Extract")
    summary_out = gr.Textbox(label="Quick summary", lines=6)
    json_out = gr.File(label="Download resume.json")
    report_out = gr.File(label="Download report.md")

    run_btn.click(fn=run_extraction, inputs=[file_in], outputs=[summary_out, json_out, report_out])

if __name__ == "__main__":
    demo.launch(share=True, show_api=False)
