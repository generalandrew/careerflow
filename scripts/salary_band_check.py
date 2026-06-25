#!/usr/bin/env python3
"""
salary_band_check.py - Read locally stored salary bands and surface a
defensible salary range for a given role + company + level + market.

This is a thin local tool. Web-sourced lookups (Levels.fyi, Glassdoor, etc.)
are expected to be performed by Claude via WebSearch and merged with the
output of this script in chat. Claude then optionally calls --add-to-bands
to persist new research.

Usage:
    python3 scripts/salary_band_check.py \
        --role "Senior Solutions Engineer" \
        [--company "Acme"] \
        [--level "Senior"] \
        [--market "Dallas, TX"] \
        [--save <md path>] \
        [--add-to-bands]      \
        [--new-band-json '<json>']
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP_PATH = ROOT / "master" / "experience.json"


def load_local_bands():
    if not EXP_PATH.exists():
        return [], {}
    exp = json.loads(EXP_PATH.read_text())
    bands = exp.get("preferences", {}).get("salary_bands", {}).get("entries", [])
    targets = exp.get("preferences", {}).get("compensation_targets", {})
    return bands, targets


def match_local(bands, role=None, company=None, level=None, market=None):
    def matches(b):
        if role and role.lower() not in (b.get("title", "") or "").lower():
            return False
        if company and company.lower() not in (b.get("company", "") or "").lower():
            return False
        if level and level.lower() not in (b.get("level", "") or "").lower():
            return False
        if market and market.lower() not in (b.get("market", "") or "").lower():
            return False
        return True
    return [b for b in bands if matches(b)]


def summarize(matches):
    if not matches:
        return {"count": 0}
    base_mins = [b["base_min"] for b in matches if b.get("base_min")]
    base_maxs = [b["base_max"] for b in matches if b.get("base_max")]
    ote_mins = [b["ote_min"] for b in matches if b.get("ote_min")]
    ote_maxs = [b["ote_max"] for b in matches if b.get("ote_max")]
    return {
        "count": len(matches),
        "base_floor": min(base_mins) if base_mins else None,
        "base_median": sorted(base_mins)[len(base_mins) // 2] if base_mins else None,
        "base_ceiling": max(base_maxs) if base_maxs else None,
        "ote_floor": min(ote_mins) if ote_mins else None,
        "ote_median": sorted(ote_mins)[len(ote_mins) // 2] if ote_mins else None,
        "ote_ceiling": max(ote_maxs) if ote_maxs else None,
        "entries": matches,
    }


def add_band(new_entry):
    if not EXP_PATH.exists():
        sys.stderr.write("experience.json not found\n"); return 2
    exp = json.loads(EXP_PATH.read_text())
    exp.setdefault("preferences", {}).setdefault("salary_bands", {}).setdefault("entries", []).append(new_entry)
    EXP_PATH.write_text(json.dumps(exp, indent=2))
    print(f"Added band entry to {EXP_PATH}")
    return 0


def write_research_md(path, role, company, level, market, summary, targets):
    md = []
    md.append(f"# Salary Band Research, {role}")
    md.append(f"_Captured: {datetime.date.today().isoformat()}_\n")
    if company: md.append(f"**Company**: {company}  ")
    if level:   md.append(f"**Level**: {level}  ")
    if market:  md.append(f"**Market**: {market}  ")
    md.append("")
    md.append("## Locally Stored Matching Bands")
    if summary["count"]:
        md.append(f"- Count: {summary['count']}")
        if summary.get("base_floor"):
            md.append(f"- Base range, floor / median / ceiling: ${summary['base_floor']:,} / ${summary['base_median']:,} / ${summary['base_ceiling']:,}")
        if summary.get("ote_floor"):
            md.append(f"- OTE range, floor / median / ceiling: ${summary['ote_floor']:,} / ${summary['ote_median']:,} / ${summary['ote_ceiling']:,}")
    else:
        md.append("- No matching local bands. Claude should WebSearch Levels.fyi, Built In, Glassdoor to populate.")
    md.append("")
    md.append("## User Compensation Targets (from experience.json)")
    for k, v in targets.items():
        if v not in (None, "", []):
            md.append(f"- **{k}**: {v}")
    md.append("")
    md.append("## Web-Sourced Bands (Claude should populate during chat)")
    md.append("- Levels.fyi: TBD")
    md.append("- Built In: TBD")
    md.append("- Glassdoor: TBD")
    md.append("")
    md.append("## Recommended Anchor")
    md.append("(Claude synthesizes from local + web sources, considering user targets.)")
    Path(path).write_text("\n".join(md))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role")
    ap.add_argument("--company")
    ap.add_argument("--level")
    ap.add_argument("--market")
    ap.add_argument("--save", help="Write Markdown research file to this path")
    ap.add_argument("--add-to-bands", action="store_true", help="Append --new-band-json to experience.json bands")
    ap.add_argument("--new-band-json", help="JSON string for new band entry")
    args = ap.parse_args()

    if args.add_to_bands:
        if not args.new_band_json:
            sys.stderr.write("--new-band-json required with --add-to-bands\n"); return 2
        try:
            entry = json.loads(args.new_band_json)
        except Exception as e:
            sys.stderr.write(f"Invalid JSON: {e}\n"); return 2
        return add_band(entry)

    if not args.role:
        sys.stderr.write("--role required for lookup\n"); return 2

    bands, targets = load_local_bands()
    matches = match_local(bands, args.role, args.company, args.level, args.market)
    summary = summarize(matches)

    print(json.dumps({
        "lookup": {"role": args.role, "company": args.company, "level": args.level, "market": args.market},
        "local_summary": summary,
        "user_targets": targets,
    }, indent=2))

    if args.save:
        write_research_md(args.save, args.role, args.company, args.level, args.market, summary, targets)
        print(f"Wrote {args.save}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
