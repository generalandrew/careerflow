#!/usr/bin/env python3
"""
quarterly_career_review.py - Prompt the user to update master/experience.json
with new wins, mentees promoted, new skills, public artifacts. Without this
prompt, profiles atrophy. Outputs a diff of what was added during the quarter.

This script does two things:
  1. Generates a quarterly review prompt that Claude can walk the user through.
  2. Snapshots master/experience.json so the next quarterly review can show a diff.

Usage:
    python3 scripts/quarterly_career_review.py [--mode prompt|diff|snapshot]
"""
import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP_PATH = ROOT / "master" / "experience.json"
SNAPSHOTS_DIR = ROOT / "master" / "snapshots"
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def latest_snapshot():
    snaps = sorted(SNAPSHOTS_DIR.glob("experience_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return snaps[0] if snaps else None


def make_snapshot():
    if not EXP_PATH.exists():
        sys.stderr.write("experience.json not found\n")
        return 2
    today = datetime.date.today().isoformat()
    snap_path = SNAPSHOTS_DIR / f"experience_{today}.json"
    shutil.copy(EXP_PATH, snap_path)
    print(f"Snapshot created: {snap_path}")
    return 0


def compute_diff(old_path, new_path):
    old = json.loads(old_path.read_text())
    new = json.loads(new_path.read_text())
    diffs = {
        "new_roles": [],
        "new_bullets_per_role": {},
        "new_skills": [],
        "new_certifications": [],
        "new_public_artifacts": [],
        "leadership_signal_changes": {},
    }

    old_companies = {r["company"] for r in old.get("roles", [])}
    for r in new.get("roles", []):
        if r["company"] not in old_companies:
            diffs["new_roles"].append(r.get("title", "") + " at " + r["company"])
            continue
        # Same company, look for new bullets
        old_role = next((x for x in old.get("roles", []) if x["company"] == r["company"]), {})
        old_bullets = set(x if isinstance(x, str) else x.get("text", "") for x in old_role.get("bullets", []))
        new_bullets = [b for b in r.get("bullets", []) if (b if isinstance(b, str) else b.get("text", "")) not in old_bullets]
        if new_bullets:
            diffs["new_bullets_per_role"][r["company"]] = new_bullets

    old_skills = set()
    for cat, items in (old.get("skills") or {}).items():
        old_skills.update(items if isinstance(items, list) else [])
    new_skills_all = set()
    for cat, items in (new.get("skills") or {}).items():
        new_skills_all.update(items if isinstance(items, list) else [])
    diffs["new_skills"] = sorted(new_skills_all - old_skills)

    diffs["new_certifications"] = list(set(new.get("certifications", [])) - set(old.get("certifications", [])))

    old_artifacts = old.get("public_artifacts", {})
    new_artifacts = new.get("public_artifacts", {})
    for k, v in new_artifacts.items():
        if isinstance(v, list):
            old_v = old_artifacts.get(k, [])
            new_items = [item for item in v if item not in old_v]
            if new_items:
                diffs["new_public_artifacts"].extend([f"{k}: {item}" for item in new_items])

    old_ls = old.get("leadership_signal", {})
    new_ls = new.get("leadership_signal", {})
    for k, v in new_ls.items():
        if old_ls.get(k) != v:
            diffs["leadership_signal_changes"][k] = {"from": old_ls.get(k), "to": v}

    return diffs


def emit_prompt():
    today = datetime.date.today()
    quarter = (today.month - 1) // 3 + 1
    md = []
    md.append(f"# Quarterly Career Review, Q{quarter} {today.year}")
    md.append("")
    md.append("Claude should walk through these prompts with the user, capturing answers")
    md.append("into master/experience.json. After the review, run with --mode snapshot")
    md.append("to create a snapshot, then --mode diff in three months to surface the diff.")
    md.append("")
    md.append("## Prompts")
    md.append("")
    md.append("1. Since your last review, what new project, pursuit, or initiative are you most proud of? Describe in STAR format.")
    md.append("2. Any new quantified outcome to add to an existing role (revenue, pipeline, deal closed, team size grown)?")
    md.append("3. Any mentees who got promoted, took a new role, or had a major win this quarter?")
    md.append("4. New skills, frameworks, or platforms you have hands-on competence with now that you didn't 90 days ago?")
    md.append("5. New certifications earned, started, or planned?")
    md.append("6. Any public artifacts (talk given, article published, podcast appearance, open source contribution)?")
    md.append("7. Has your leadership scope changed (direct reports, matrix, team headcount)?")
    md.append("8. Has your career motivation shifted? Are your targeting profile (job types, seniority, geography, compensation) still accurate?")
    md.append("9. Any new salary band data to add to your local research (offers received, accepted ranges)?")
    md.append("10. What is your one-line career narrative right now? (Used to update the resume headline.)")
    md.append("")
    md.append("After capturing answers into experience.json, run:")
    md.append("```")
    md.append("python3 scripts/quarterly_career_review.py --mode snapshot")
    md.append("```")
    md.append("to lock in this quarter's snapshot for next quarter's diff.")
    review_path = ROOT / f"quarterly_review_prompt_{today.isoformat()}.md"
    review_path.write_text("\n".join(md))
    print(f"Wrote {review_path}")


def emit_diff():
    if not EXP_PATH.exists():
        sys.stderr.write("experience.json not found\n")
        return 2
    snap = latest_snapshot()
    if not snap:
        print("No prior snapshot found. Run --mode snapshot to create one for next quarter's diff.")
        return 0
    diffs = compute_diff(snap, EXP_PATH)
    today = datetime.date.today()
    md = []
    md.append(f"# Quarterly Career Diff, {today.isoformat()}")
    md.append(f"_Comparing against snapshot: {snap.name}_")
    md.append("")
    if diffs["new_roles"]:
        md.append("## New Roles")
        for r in diffs["new_roles"]:
            md.append(f"- {r}")
        md.append("")
    if diffs["new_bullets_per_role"]:
        md.append("## New Bullets Added to Existing Roles")
        for company, bullets in diffs["new_bullets_per_role"].items():
            md.append(f"### {company}")
            for b in bullets:
                txt = b if isinstance(b, str) else b.get("text", "")
                md.append(f"- {txt}")
        md.append("")
    if diffs["new_skills"]:
        md.append("## New Skills")
        for s in diffs["new_skills"]:
            md.append(f"- {s}")
        md.append("")
    if diffs["new_certifications"]:
        md.append("## New Certifications")
        for c in diffs["new_certifications"]:
            md.append(f"- {c}")
        md.append("")
    if diffs["new_public_artifacts"]:
        md.append("## New Public Artifacts")
        for a in diffs["new_public_artifacts"]:
            md.append(f"- {a}")
        md.append("")
    if diffs["leadership_signal_changes"]:
        md.append("## Leadership Signal Changes")
        for k, v in diffs["leadership_signal_changes"].items():
            md.append(f"- **{k}**: {v['from']} -> {v['to']}")
        md.append("")
    if not any([diffs["new_roles"], diffs["new_bullets_per_role"], diffs["new_skills"], diffs["new_certifications"], diffs["new_public_artifacts"], diffs["leadership_signal_changes"]]):
        md.append("No diffs detected since last snapshot. Either nothing changed, or the quarterly review hasn't captured the changes yet.")
    out_path = ROOT / f"quarterly_career_diff_{today.isoformat()}.md"
    out_path.write_text("\n".join(md))
    print(f"Wrote {out_path}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["prompt", "snapshot", "diff"], default="prompt")
    args = ap.parse_args()
    if args.mode == "prompt":
        emit_prompt()
        return 0
    elif args.mode == "snapshot":
        return make_snapshot()
    elif args.mode == "diff":
        return emit_diff()


if __name__ == "__main__":
    sys.exit(main())
