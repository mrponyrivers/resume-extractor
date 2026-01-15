import re
from pathlib import Path

from pypdf import PdfReader


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
URL_RE = re.compile(r"(https?://[^\s]+)", re.IGNORECASE)

# Simple starter skills list (expand over time)
SKILLS = {
    "python", "sql", "excel", "google sheets", "git", "github", "api", "json", "csv",
    "pandas", "automation", "workflow", "streamlit", "gradio",
    "linux", "bash", "docker", "aws",
}


def read_text_from_pdf(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def read_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input not found: {path}")

    if p.suffix.lower() == ".pdf":
        return read_text_from_pdf(p)

    # treat everything else as text
    return p.read_text(encoding="utf-8", errors="ignore")


def guess_name(text: str) -> str:
    # Heuristic: first non-empty line that isn't obviously an email/phone/url
    for line in [l.strip() for l in text.splitlines()]:
        if not line:
            continue
        if EMAIL_RE.search(line) or PHONE_RE.search(line) or URL_RE.search(line):
            continue
        if len(line) > 60:
            continue
        # avoid headings like "RESUME"
        if line.lower() in {"resume", "curriculum vitae", "cv"}:
            continue
        return line
    return ""


def extract_contacts(text: str) -> dict:
    emails = list(dict.fromkeys(EMAIL_RE.findall(text)))
    phones = list(dict.fromkeys([m[0] if isinstance(m, tuple) else m for m in PHONE_RE.findall(text)]))
    urls = list(dict.fromkeys(URL_RE.findall(text)))

    linkedin = ""
    github = ""
    for u in urls:
        low = u.lower()
        if "linkedin.com" in low and not linkedin:
            linkedin = u
        if "github.com" in low and not github:
            github = u

    return {
        "emails": emails,
        "phones": phones,
        "urls": urls,
        "linkedin": linkedin,
        "github": github,
    }


def extract_skills(text: str) -> list:
    t = text.lower()
    found = sorted({s for s in SKILLS if s in t})
    return found


def extract_sections(text: str) -> dict:
    # Very light heuristics for v1
    lines = [l.strip() for l in text.splitlines()]
    education = []
    experience = []

    in_edu = False
    in_exp = False

    for line in lines:
        low = line.lower()
        if not line:
            continue

        if low.startswith("education"):
            in_edu, in_exp = True, False
            continue
        if low.startswith("experience") or low.startswith("work experience"):
            in_exp, in_edu = True, False
            continue
        if low.startswith("skills"):
            in_edu = in_exp = False
            continue

        if in_edu:
            education.append(line)
        if in_exp:
            experience.append(line)

    return {"education_lines": education[:20], "experience_lines": experience[:40]}


def extract_resume(path: str) -> dict:
    text = read_text(path)
    name = guess_name(text)
    contacts = extract_contacts(text)
    skills = extract_skills(text)
    sections = extract_sections(text)

    return {
        "source_file": path,
        "name_guess": name,
        "contacts": contacts,
        "skills_found": skills,
        "education_lines": sections["education_lines"],
        "experience_lines": sections["experience_lines"],
        "notes": [
            "Local-only heuristic extraction (v1).",
            "Improve by expanding SKILLS list and smarter section parsing.",
        ],
    }
