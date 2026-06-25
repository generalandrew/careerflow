#!/usr/bin/env python3
"""
write_interview_prep.py - Write interview_prep.md for an application.

Reads JSON on stdin:
  {
    "app_dir": "/abs/path",
    "company": "Acme",
    "role": "Senior Solutions Engineer",
    "background": "Recent context on company/role",       (optional)
    "questions": [
      {
        "q": "Walk me through your largest enterprise pursuit",
        "rationale": "Tests deal ownership credibility",
        "talking_points": ["...", "..."]
      },
      ...
    ],
    "questions_to_ask_them": ["...", "..."],              (optional)
    "star_stories": [{"name": "...", "summary": "..."}],  (optional)
    "red_flag_handling": [{"if": "...", "then": "..."}],  (optional)
    "close_script": "..."                                  (optional)
  }
"""
import sys, json, datetime
from pathlib import Path


def main():
    p = json.load(sys.stdin)
    app_dir = Path(p["app_dir"]).resolve()
    md = []
    md.append(f"# Interview Prep, {p.get('company','?')} / {p.get('role','?')}")
    md.append(f"_Generated: {datetime.date.today().isoformat()}_\n")

    if p.get("background"):
        md.append("## Background")
        md.append(p["background"] + "\n")

    if p.get("questions"):
        md.append("## Likely Questions and How to Answer\n")
        for i, q in enumerate(p["questions"], 1):
            md.append(f"### {i}. {q.get('q','')}")
            if q.get("rationale"):
                md.append(f"_Why this matters:_ {q['rationale']}\n")
            for tp in q.get("talking_points", []):
                md.append(f"- {tp}")
            md.append("")

    if p.get("questions_to_ask_them"):
        md.append("## Questions to Ask Them")
        for q in p["questions_to_ask_them"]:
            md.append(f"- {q}")
        md.append("")

    if p.get("star_stories"):
        md.append("## STAR Stories Ready to Deploy")
        for s in p["star_stories"]:
            md.append(f"- **{s.get('name','?')}:** {s.get('summary','')}")
        md.append("")

    if p.get("red_flag_handling"):
        md.append("## Red Flag Handling")
        for r in p["red_flag_handling"]:
            md.append(f"- **If** {r.get('if','')} **then** {r.get('then','')}")
        md.append("")

    if p.get("close_script"):
        md.append("## Close Script")
        md.append(p["close_script"] + "\n")

    out = app_dir / "interview_prep.md"
    out.write_text("\n".join(md))
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
