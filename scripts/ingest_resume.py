#!/usr/bin/env python3
"""
ingest_resume.py - Parse a resume PDF or DOCX and extract structured data
into a draft tailored.json-style dict, written as JSON to stdout or to a
file with --out.

Best-effort, regex + heuristic-based. The result is a starting point for
Claude to review with the user during onboarding, not a finished profile.

Usage:
    python3 scripts/ingest_resume.py <resume_path> [--out resume_draft.json]
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path


def extract_text_pdf(path):
    """Try PyPDF2 / pdfplumber for PDF parsing."""
    try:
        import pdfplumber
        out = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                out.append(page.extract_text() or "")
        return "\n".join(out)
    except ImportError:
        pass
    try:
        from PyPDF2 import PdfReader
        out = []
        reader = PdfReader(str(path))
        for page in reader.pages:
            out.append(page.extract_text() or "")
        return "\n".join(out)
    except ImportError:
        sys.stderr.write(
            "PDF parsing requires pdfplumber or PyPDF2.\n"
            "Install with: pip install pdfplumber\n"
        )
        return ""


def extract_text_docx(path):
    """Extract text from a DOCX by reading word/document.xml."""
    try:
        with zipfile.ZipFile(path) as z:
            data = z.read("word/document.xml").decode("utf-8", errors="ignore")
        text = re.sub(r"<[^>]+>", " ", data)
        text = re.sub(r"\s+", " ", text)
        return text
    except Exception as e:
        sys.stderr.write(f"DOCX extraction failed: {e}\n")
        return ""


def extract_text(path):
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        return extract_text_pdf(p)
    if p.suffix.lower() in (".docx", ".doc"):
        return extract_text_docx(p)
    return p.read_text(errors="ignore")


# Heuristic extractors
EMAIL_RE = re.compile(r"[\w\.\-]+@[\w\.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"\b\d{3}[\-\s\.]?\d{3}[\-\s\.]?\d{4}\b")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w\-]+", re.IGNORECASE)
GITHUB_RE = re.compile(r"github\.com/[\w\-]+", re.IGNORECASE)
LOCATION_RE = re.compile(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)?),\s*([A-Z]{2})\b")
DATE_RANGE_RE = re.compile(
    r"\b([A-Z][a-z]{2,9})\s+(\d{4})\s*[-–—]\s*(?:([A-Z][a-z]{2,9})\s+(\d{4})|Present|Current)\b"
)
SECTION_HEADERS = ["experience", "professional experience", "work experience", "employment",
                   "education", "skills", "technical skills", "certifications", "projects",
                   "publications", "languages", "volunteer", "awards", "summary", "objective"]


def find_personal_info(text):
    info = {}
    m = EMAIL_RE.search(text)
    if m: info["email"] = m.group(0)
    m = PHONE_RE.search(text)
    if m: info["phone"] = m.group(0)
    m = LINKEDIN_RE.search(text)
    if m: info["linkedin"] = m.group(0)
    m = GITHUB_RE.search(text)
    if m: info["github"] = m.group(0)
    m = LOCATION_RE.search(text)
    if m: info["location"] = m.group(0)
    # Name: usually the first non-empty line
    first_line = next((l.strip() for l in text.splitlines() if l.strip()), "")
    if first_line and len(first_line) < 60 and "@" not in first_line:
        info["name"] = first_line
    return info


def split_sections(text):
    """Try to split the resume into sections by headers."""
    lines = text.splitlines()
    sections = {}
    current_header = "_top"
    sections[current_header] = []
    for line in lines:
        stripped = line.strip().lower()
        if any(stripped == h or stripped.startswith(h + " ") or stripped.endswith(" " + h) for h in SECTION_HEADERS) and len(stripped) < 50:
            current_header = stripped
            sections[current_header] = []
        else:
            sections[current_header].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items() if v}


def extract_role_blocks(experience_text):
    """Find date ranges and assume each marks a role boundary."""
    matches = list(DATE_RANGE_RE.finditer(experience_text))
    blocks = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(experience_text)
        # The role title and company usually appear in the lines just above the date
        block_text = experience_text[max(0, start - 200):end]
        date_str = m.group(0)
        # Bullets, lines starting with bullet markers or capital letters
        bullets = re.findall(r"(?:^|\n)\s*[•\-\*]\s*(.+)", block_text)
        blocks.append({
            "date_range": date_str,
            "raw_block": block_text.strip(),
            "bullets": [b.strip() for b in bullets if len(b.strip()) > 10],
        })
    return blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("resume_path")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    text = extract_text(args.resume_path)
    if not text:
        sys.stderr.write("No text extracted.\n"); return 2

    info = find_personal_info(text)
    sections = split_sections(text)
    exp_text = (sections.get("professional experience")
                or sections.get("experience")
                or sections.get("work experience")
                or sections.get("employment")
                or "")
    roles = extract_role_blocks(exp_text)

    draft = {
        "_source": "resume",
        "personal": info,
        "raw_sections": sections,
        "roles_draft": roles,
        "notes": "Best-effort extraction. Claude should review with user during onboarding and confirm or correct each field.",
    }

    out = json.dumps(draft, indent=2)
    if args.out:
        Path(args.out).write_text(out)
        print(f"Wrote {args.out}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
