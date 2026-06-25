#!/usr/bin/env python3
"""
nda_audit.py - Audit a resume or tailored.json for accidental customer name leaks.

Reads master/experience.json to get the protected employer list (from nda_rule
field). Scans the target file for any company names that appear to be
customers of a protected employer, flags them, returns exit code 1 if any leaks
are found.

Usage:
    python3 scripts/nda_audit.py <tailored.json or .docx or .md>
    python3 scripts/nda_audit.py <app_dir>     # scans all packet files

Common usage in the workflow:
    python3 scripts/nda_audit.py applications/2026-01-15_Acme_Director
"""
import argparse, json, re, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP_PATH = ROOT / "master" / "experience.json"

# Common Fortune 500 / global enterprise customer names to flag if they appear
# in a resume tied to a protected employer. This is a default seed list; users
# customize it via master/experience.json -> nda_customer_watchlist
DEFAULT_CUSTOMER_WATCHLIST = [
    # Banking / FSI
    "JPMorgan", "JPMC", "Goldman Sachs", "Wells Fargo", "Bank of America", "BofA", "Citi", "Citibank",
    "Capital One", "Morgan Stanley", "American Express", "Amex", "PNC", "U.S. Bank", "USAA",
    "Charles Schwab", "Fidelity", "Vanguard", "BlackRock",
    # Healthcare
    "UnitedHealth", "Kaiser Permanente", "Anthem", "Humana", "Cigna", "CVS Health", "Walgreens",
    "Pfizer", "Merck", "Johnson and Johnson", "AbbVie", "Eli Lilly",
    # Retail
    "Walmart", "Target", "Costco", "Home Depot", "Lowe's", "Kroger", "Best Buy", "Macy's",
    "Nordstrom", "Victoria's Secret", "L Brands",
    # Media / Entertainment
    "Disney", "Comcast", "NBCUniversal", "Paramount", "Warner Bros", "Sony Pictures",
    "Netflix", "Spotify", "Live Nation",
    # Tech / Enterprise
    "Microsoft", "Google", "Amazon", "Meta", "Apple",
    # Sports leagues (anonymized as "professional sports franchise")
    "NHL", "NFL", "NBA", "MLB", "MLS",
]


def load_protected_list():
    if not EXP_PATH.exists():
        return [], DEFAULT_CUSTOMER_WATCHLIST
    try:
        exp = json.loads(EXP_PATH.read_text())
        protected_employers = []
        nda_rule = exp.get("nda_rule", "")
        # Try structured field first
        if isinstance(exp.get("protected_employers"), list):
            protected_employers = exp["protected_employers"]
        watchlist = exp.get("nda_customer_watchlist", DEFAULT_CUSTOMER_WATCHLIST)
        return protected_employers, watchlist
    except Exception:
        return [], DEFAULT_CUSTOMER_WATCHLIST


def extract_text_from_docx(path):
    try:
        with zipfile.ZipFile(path) as z:
            data = z.read("word/document.xml").decode("utf-8", errors="ignore")
        text = re.sub(r"<[^>]+>", " ", data)
        text = re.sub(r"\s+", " ", text)
        return text
    except Exception as e:
        return f""


def get_text(path):
    if path.suffix == ".json":
        try:
            return json.dumps(json.loads(path.read_text()))
        except Exception:
            return path.read_text(errors="ignore")
    if path.suffix == ".docx":
        return extract_text_from_docx(path)
    if path.suffix in (".md", ".txt", ".html"):
        return path.read_text(errors="ignore")
    return ""


def scan_text(text, watchlist):
    found = []
    for name in watchlist:
        if re.search(rf"\b{re.escape(name)}\b", text, re.IGNORECASE):
            found.append(name)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    args = ap.parse_args()

    target = Path(args.path).resolve()
    if not target.exists():
        sys.stderr.write(f"Path not found: {target}\n"); return 2

    protected_employers, watchlist = load_protected_list()

    files_to_scan = []
    if target.is_dir():
        for ext in ("*.docx", "tailored.json", "*_summary.md", "interview_prep.md", "CoverLetter*.docx"):
            files_to_scan.extend(target.glob(ext))
    else:
        files_to_scan = [target]

    any_leaks = False
    for f in files_to_scan:
        text = get_text(f)
        if not text:
            continue
        leaks = scan_text(text, watchlist)
        if leaks:
            any_leaks = True
            print(f"\n[LEAK CANDIDATES] {f.name}")
            for name in leaks:
                print(f"  - {name}")
    if not any_leaks:
        print(f"No protected customer names detected in {target.name}")
        return 0

    print()
    print("Action: review each leak candidate. If the name is a true customer of a protected employer,")
    print("anonymize the reference (e.g., 'professional sports franchise', 'global shipping customer').")
    print("If the name is the employer itself (not a customer), it is OK to leave.")
    if protected_employers:
        print(f"\nProtected employers configured: {', '.join(protected_employers)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
