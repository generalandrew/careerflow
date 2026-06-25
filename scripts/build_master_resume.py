#!/usr/bin/env python3
"""
build_master_resume.py - Generate a full master resume DOCX directly from
master/experience.json. Used for cold outreach and as a long-form reference.

The master resume includes ALL roles and ALL bullets from experience.json,
without tailoring to any specific job description.

Usage:
    python3 scripts/build_master_resume.py
        [--out master/MasterResume.docx]
        [--conservative]
"""
import argparse, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP_PATH = ROOT / "master" / "experience.json"
DEFAULT_OUT = ROOT / "master" / "MasterResume.docx"
BUILD_RESUME = ROOT / "scripts" / "build_resume.js"
NODE_PATH = os.environ.get("NODE_PATH", str(ROOT / "node_modules"))


def experience_to_tailored(exp):
    """Convert master/experience.json shape to the tailored.json shape that
    build_resume.js expects, preserving all roles and bullets."""
    personal = exp.get("personal", {})
    summary_options = exp.get("summary_options", {})
    summary = summary_options.get("narrative") or summary_options.get("director") or summary_options.get("vp") or ""

    roles_out = []
    for r in exp.get("roles", []):
        roles_out.append({
            "company": r.get("company", ""),
            "title": r.get("title", ""),
            "client": r.get("client", ""),
            "dates": format_dates(r),
            "scope": r.get("scope", ""),
            "bullets": [b if isinstance(b, str) else b.get("text", "") for b in r.get("bullets", [])],
        })

    skills = exp.get("skills", {})
    # If skills is a dict of categories, pass through; if list, wrap
    if isinstance(skills, list):
        skills = {"Skills": skills}

    return {
        "_company": "Master Resume",
        "_role": "All Experience",
        "personal": personal,
        "headline": (personal.get("headline_options", [""]) or [""])[0],
        "summary": summary,
        "core_competencies": exp.get("core_competencies", []),
        "roles": roles_out,
        "skills": skills,
        "education": exp.get("education", []),
        "certifications": exp.get("certifications", []),
    }


def format_dates(role):
    """Format start/end into 'Mar 2018 - Apr 2023' or 'Mar 2018 - Present'."""
    start = role.get("start", "")
    end = role.get("end")
    if not start:
        return role.get("dates", "")
    def fmt(yyyymm):
        import calendar
        try:
            y, m = yyyymm.split("-")
            m_int = int(m)
            return f"{calendar.month_abbr[m_int]} {y}"
        except Exception:
            return yyyymm
    start_str = fmt(start)
    end_str = "Present" if end in (None, "", "Present", "present") else fmt(end)
    return f"{start_str} - {end_str}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--conservative", action="store_true")
    args = ap.parse_args()

    if not EXP_PATH.exists():
        sys.stderr.write(f"experience.json not found at {EXP_PATH}\n")
        return 2

    with open(EXP_PATH) as f:
        exp = json.load(f)

    tailored = experience_to_tailored(exp)
    out_docx = Path(args.out).resolve()
    out_docx.parent.mkdir(parents=True, exist_ok=True)

    # Write a temp tailored.json next to the output
    tmp_json = out_docx.with_suffix(".tailored.json")
    tmp_json.write_text(json.dumps(tailored, indent=2))

    env = os.environ.copy()
    env["NODE_PATH"] = NODE_PATH
    cmd = ["node", str(BUILD_RESUME), str(tmp_json), str(out_docx)]
    if args.conservative:
        cmd.append("--conservative")
    subprocess.run(cmd, check=True, env=env)

    # Clean up the temp tailored.json
    try:
        tmp_json.unlink()
    except Exception:
        pass

    print(f"Wrote master resume to {out_docx}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
