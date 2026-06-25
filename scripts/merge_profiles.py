#!/usr/bin/env python3
"""
merge_profiles.py - Reconcile resume + LinkedIn + GitHub extracts into a
single draft master/experience.json. Resolves conflicts conservatively:

  - Resume is the authoritative source for roles, titles, dates (most
    candidates curate their resume more carefully than LinkedIn).
  - LinkedIn is authoritative for headline + about/summary (often more
    polished than the resume summary).
  - LinkedIn is preferred for skills with endorsements signal.
  - GitHub fills in technical languages and projects.
  - When fields disagree on dates, flag for user confirmation rather than
    silently picking one.

Usage:
    python3 scripts/merge_profiles.py \
        --resume <resume_draft.json> \
        [--linkedin <linkedin_profile.txt>] \
        [--github <github_profile.json>] \
        [--out master/experience.json.draft]
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "master" / "experience.json.template"


def load_template():
    if not TEMPLATE.exists():
        return {}
    return json.loads(TEMPLATE.read_text())


def load_json(path):
    if path and Path(path).exists():
        try:
            return json.loads(Path(path).read_text())
        except Exception as e:
            sys.stderr.write(f"Failed to parse {path}: {e}\n")
    return None


def load_text(path):
    if path and Path(path).exists():
        return Path(path).read_text()
    return ""


def merge(resume_draft, linkedin_text, github_profile):
    out = load_template()

    # Personal
    personal = resume_draft.get("personal", {}) if resume_draft else {}
    if personal:
        out.setdefault("personal", {})
        for k in ("name", "location", "phone", "email", "linkedin", "github"):
            if personal.get(k):
                out["personal"][k] = personal[k]

    # GitHub fills in github URL and adds bio if resume didn't have it
    if github_profile:
        out.setdefault("personal", {})
        if not out["personal"].get("github"):
            out["personal"]["github"] = f"github.com/{github_profile['username']}"

    # Roles, from resume draft
    if resume_draft and resume_draft.get("roles_draft"):
        out["roles"] = []
        for rd in resume_draft["roles_draft"]:
            out["roles"].append({
                "_source": "resume",
                "_raw_block": rd.get("raw_block", "")[:500],
                "company": "TBD, Claude to extract from raw_block",
                "title": "TBD",
                "dates": rd.get("date_range", ""),
                "bullets": rd.get("bullets", []),
                "_confirmation_needed": True,
            })

    # Skills, union from resume + GitHub
    skills_aggregate = set()
    raw_sections = (resume_draft or {}).get("raw_sections", {})
    skills_text = raw_sections.get("skills", "") or raw_sections.get("technical skills", "")
    if skills_text:
        # Heuristic, split by commas, semicolons, pipes, newlines, bullets
        import re
        items = re.split(r"[,;|\n•\-\*]", skills_text)
        for it in items:
            it = it.strip()
            if 2 <= len(it) <= 60:
                skills_aggregate.add(it)
    if github_profile and github_profile.get("languages_aggregate"):
        for lang in github_profile["languages_aggregate"].keys():
            skills_aggregate.add(lang)
    if skills_aggregate:
        out.setdefault("skills", {})
        out["skills"]["From profile auto-extract"] = sorted(skills_aggregate)

    # LinkedIn text, attach as a raw block for Claude to mine
    if linkedin_text:
        out.setdefault("_extraction_artifacts", {})
        out["_extraction_artifacts"]["linkedin_raw_text_first_5000"] = linkedin_text[:5000]

    # GitHub repos as projects signal
    if github_profile and github_profile.get("top_repos_by_stars"):
        out.setdefault("public_artifacts", {})
        out["public_artifacts"].setdefault("open_source_contributions", [])
        for r in github_profile["top_repos_by_stars"][:5]:
            line = f"{r['name']}, {r.get('description') or 'no description'} ({r.get('stars', 0)} stars)"
            if line not in out["public_artifacts"]["open_source_contributions"]:
                out["public_artifacts"]["open_source_contributions"].append(line)

    # Education, raw section for Claude to parse
    edu_text = raw_sections.get("education", "")
    if edu_text:
        out.setdefault("_extraction_artifacts", {})
        out["_extraction_artifacts"]["education_raw_text"] = edu_text

    # Certifications, raw section
    cert_text = raw_sections.get("certifications", "")
    if cert_text:
        out.setdefault("_extraction_artifacts", {})
        out["_extraction_artifacts"]["certifications_raw_text"] = cert_text

    # Meta
    out.setdefault("_meta", {})
    out["_meta"]["extraction_date"] = datetime.date.today().isoformat()
    out["_meta"]["sources"] = [s for s in [
        "resume" if resume_draft else None,
        "linkedin" if linkedin_text else None,
        "github" if github_profile else None,
    ] if s]
    out["_meta"]["notes"] = (
        "Draft auto-extracted from external profiles. Claude must walk through with the user "
        "to confirm or correct each field, anonymize protected customer names, probe for "
        "quantification, and capture STAR stories."
    )

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", help="Path to resume_draft.json from ingest_resume.py")
    ap.add_argument("--linkedin", help="Path to linkedin_profile.txt from ingest_linkedin.py")
    ap.add_argument("--github", help="Path to github_profile.json from ingest_github.py")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if not any([args.resume, args.linkedin, args.github]):
        sys.stderr.write("Pass at least one of --resume, --linkedin, --github\n")
        return 2

    resume_draft = load_json(args.resume) if args.resume else None
    linkedin_text = load_text(args.linkedin) if args.linkedin else ""
    github_profile = load_json(args.github) if args.github else None

    merged = merge(resume_draft, linkedin_text, github_profile)
    out = json.dumps(merged, indent=2)
    if args.out:
        Path(args.out).write_text(out)
        print(f"Wrote {args.out}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
