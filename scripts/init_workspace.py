#!/usr/bin/env python3
"""
init_workspace.py
Generate an empty applications.xlsx with the canonical schema header row.

Usage:
    python3 scripts/init_workspace.py --xlsx /path/to/applications.xlsx
"""
import argparse
import sys
from pathlib import Path


HEADERS = [
    "Date Applied",
    "Company",
    "Role",
    "URL",
    "Status",
    "Compensation",
    "Folder",
    "Contact Name",
    "Contact Email",
    "Last Touch",
    "Notes",
]


def init_xlsx(path: Path) -> int:
    try:
        import openpyxl
    except ImportError:
        sys.stderr.write("openpyxl is required, install with: pip install openpyxl\n")
        return 2
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Applications"
    ws.append(HEADERS)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    print(f"Created empty applications.xlsx at {path}")
    print(f"  Schema: {', '.join(HEADERS)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True, help="Output path for applications.xlsx")
    args = ap.parse_args()
    return init_xlsx(Path(args.xlsx).resolve())


if __name__ == "__main__":
    sys.exit(main())
