import argparse
import json
from pathlib import Path
from datetime import datetime

from resume_tool.core import extract_resume


def write_report_md(report_path: str, data: dict) -> None:
    p = Path(report_path)
    lines = []
    lines.append("# Resume Extraction Report")
    lines.append(f"- Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- Source: {data.get('source_file','')}")
    lines.append("")
    lines.append("## Name guess")
    lines.append(f"- {data.get('name_guess','')}")
    lines.append("")
    lines.append("## Contacts")
    c = data.get("contacts", {})
    lines.append(f"- Emails: {', '.join(c.get('emails', []))}")
    lines.append(f"- Phones: {', '.join(c.get('phones', []))}")
    lines.append(f"- LinkedIn: {c.get('linkedin','')}")
    lines.append(f"- GitHub: {c.get('github','')}")
    lines.append("")
    lines.append("## Skills found")
    lines.append("- " + ", ".join(data.get("skills_found", [])))
    lines.append("")
    lines.append("## Education (lines)")
    for l in data.get("education_lines", []):
        lines.append(f"- {l}")
    lines.append("")
    lines.append("## Experience (lines)")
    for l in data.get("experience_lines", []):
        lines.append(f"- {l}")
    lines.append("")
    lines.append("## Notes")
    for n in data.get("notes", []):
        lines.append(f"- {n}")

    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Resume Extractor (PDF/TXT -> JSON + report.md)")
    parser.add_argument("--input", required=True, help="Path to resume (.pdf or .txt)")
    parser.add_argument("--json", default="resume.json", help="Output JSON (default: resume.json)")
    parser.add_argument("--report", default="report.md", help="Output report (default: report.md)")
    args = parser.parse_args()

    data = extract_resume(args.input)

    Path(args.json).write_text(json.dumps(data, indent=2), encoding="utf-8")
    write_report_md(args.report, data)

    print("Done.")
    print(f"- Wrote: {args.json}")
    print(f"- Wrote: {args.report}")


if __name__ == "__main__":
    main()
