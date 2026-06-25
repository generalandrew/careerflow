#!/usr/bin/env python3
"""
apply.py - End-to-end orchestrator for a single job application.

Steps:
  1. Create application folder named YYYY-MM-DD_Company_Role
  2. Ingest posting (URL or pasted text) -> posting.html, posting.json
  3. Detect ATS from URL, write into posting.json
  4. (Caller-supplied) Build tailored.json
  5. Render resume.docx via build_resume.js (conservative variant if ATS legacy/unknown)
  6. Append row to applications.xlsx
  7. Write metadata.json

Workspace layout assumed:
    <ROOT>/
        scripts/   apply.py, ingest_posting.py, build_resume.js, ats_detector.py
        applications/
        applications.xlsx

ROOT is auto-discovered as the parent of the scripts directory.

Usage:
  python3 scripts/apply.py --url <url> --company "Acme" --role "Senior PM"
  python3 scripts/apply.py --paste --company "Acme" --role "Senior PM"
  python3 scripts/apply.py --tailored applications/<folder>/tailored.json
"""
import argparse, datetime, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_INDEX = ROOT / "applications.xlsx"
APPS_DIR = ROOT / "applications"
SCRIPTS_DIR = ROOT / "scripts"
# Allow override via env, otherwise rely on local node_modules in workspace root
NODE_PATH = os.environ.get("NODE_PATH", str(ROOT / "node_modules"))

DEFAULT_STATUS = "Draft"


def slug(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "", s)
    return s[:40]


def folder_name(company: str, role: str, date: datetime.date) -> str:
    return f"{date.isoformat()}_{slug(company)}_{slug(role)}"


def ingest(url, app_dir: Path, paste_text):
    if paste_text is not None:
        cmd = [sys.executable, str(SCRIPTS_DIR / "ingest_posting.py"), "--paste", str(app_dir)]
        subprocess.run(cmd, input=paste_text, text=True, check=True)
    else:
        cmd = [sys.executable, str(SCRIPTS_DIR / "ingest_posting.py"), url, str(app_dir)]
        subprocess.run(cmd, check=True)
    with open(app_dir / "posting.json") as f:
        return json.load(f)


def detect_ats_for_url(url):
    """Detect ATS from URL via ats_detector.py. Returns dict."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from ats_detector import detect_ats
        return detect_ats(url or "")
    except Exception as e:
        sys.stderr.write(f"ATS detector failed: {e}, defaulting to conservative\n")
        return {
            "ats": "Unknown (detector error)",
            "is_legacy": False,
            "use_conservative_render": True,
            "notes": f"Detector exception: {e}",
        }


def render_resume(tailored_path: Path, out_docx: Path, conservative: bool = False) -> None:
    env = os.environ.copy()
    env["NODE_PATH"] = NODE_PATH
    cmd = ["node", str(SCRIPTS_DIR / "build_resume.js"), str(tailored_path), str(out_docx)]
    if conservative:
        cmd.append("--conservative")
    subprocess.run(cmd, check=True, env=env)


# PDF output is intentionally not produced. DOCX is the only supported format
# per ATS optimization rules. If a future target explicitly requires PDF,
# convert manually outside the pipeline.


def get_candidate_name():
    """Look up candidate name from master/experience.json for resume filename."""
    exp_path = ROOT / "master" / "experience.json"
    if not exp_path.exists():
        return "Resume"
    try:
        with open(exp_path) as f:
            exp = json.load(f)
        name = exp.get("personal", {}).get("name", "Resume")
        return slug(name.replace(" ", ""))
    except Exception:
        return "Resume"


def append_index_row(row):
    try:
        import openpyxl
    except ImportError:
        sys.stderr.write("openpyxl required: pip install openpyxl\n")
        return
    wb = openpyxl.load_workbook(APP_INDEX)
    ws = wb.active
    headers = [c.value for c in ws[1]]
    ws.append([row.get(h, "") for h in headers])
    wb.save(APP_INDEX)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url")
    ap.add_argument("--paste", action="store_true", help="Read posting text from stdin")
    ap.add_argument("--company")
    ap.add_argument("--role")
    ap.add_argument("--tailored", help="Path to existing tailored.json; skips ingestion")
    ap.add_argument("--status", default=DEFAULT_STATUS)
    args = ap.parse_args()

    today = datetime.date.today()
    candidate_slug = get_candidate_name()

    # Mode 1: render-only from existing tailored.json
    if args.tailored:
        tpath = Path(args.tailored).resolve()
        app_dir = tpath.parent
        with open(tpath) as f:
            tailored = json.load(f)
        company = tailored.get("_company") or args.company or "Company"
        # Detect ATS from posting.json url if present
        ats_info = {"use_conservative_render": True, "ats": "Unknown", "notes": "No posting.json found"}
        posting_path = app_dir / "posting.json"
        if posting_path.exists():
            with open(posting_path) as f:
                posting = json.load(f)
            ats_info = detect_ats_for_url(posting.get("url", ""))
        elif args.url:
            ats_info = detect_ats_for_url(args.url)
        print(f"ATS detected: {ats_info['ats']} | conservative render: {ats_info['use_conservative_render']}")
        out_docx = app_dir / f"{candidate_slug}_Resume_{slug(company)}.docx"
        render_resume(tpath, out_docx, conservative=ats_info["use_conservative_render"])
        print(f"Rendered: {out_docx}")
        return 0

    # Mode 2: ingest first
    if not (args.company and args.role):
        sys.stderr.write("--company and --role required when ingesting\n")
        return 2

    app_dir = APPS_DIR / folder_name(args.company, args.role, today)
    app_dir.mkdir(parents=True, exist_ok=True)

    paste_text = sys.stdin.read() if args.paste else None
    posting = ingest(args.url, app_dir, paste_text)

    # Detect ATS from URL, write into posting.json
    ats_info = detect_ats_for_url(args.url)
    posting["ats"] = ats_info
    with open(app_dir / "posting.json", "w") as f:
        json.dump(posting, f, indent=2)
    print(f"ATS detected: {ats_info['ats']} | is_legacy: {ats_info['is_legacy']} | conservative_render: {ats_info['use_conservative_render']}")
    print(f"  Notes: {ats_info['notes']}")

    # Write metadata
    meta = {
        "date_applied": today.isoformat(),
        "company": args.company,
        "role": args.role,
        "url": args.url or "",
        "status": args.status,
        "folder": str(app_dir.relative_to(ROOT)),
        "posting_title": posting.get("title", ""),
        "keywords": posting.get("keywords", []),
        "ats": ats_info,
        "notes": ""
    }
    with open(app_dir / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    # Append index row
    append_index_row({
        "Date Applied": today.isoformat(),
        "Company": args.company,
        "Role": args.role,
        "URL": args.url or "",
        "Status": args.status,
        "Folder": str(app_dir.relative_to(ROOT)),
        "Contact Name": "",
        "Contact Email": "",
        "Last Touch": today.isoformat(),
        "Notes": "",
    })

    print(f"Created application folder: {app_dir}")
    print(f"Next: build tailored.json in that folder, then run with --tailored.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
