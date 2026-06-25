#!/usr/bin/env python3
"""
ats_detector.py

Detects the Applicant Tracking System (ATS) for a given job posting URL.
Returns metadata including whether the ATS is legacy and whether the
conservative render variant should be used.

Fail-unsafe logic, per docs/ats_optimization_rules.md:
  - If ATS is identified as legacy, use conservative render
  - If ATS cannot be identified, use conservative render
  - If ATS is identified as modern, use standard render

Usage:
    from ats_detector import detect_ats
    info = detect_ats("https://jobs.ashbyhq.com/co/uuid")
    # {"ats": "Ashby", "is_legacy": False, "use_conservative_render": False, "notes": "..."}

    # CLI usage:
    python3 scripts/ats_detector.py <url>
"""
import re
import sys
import json
from typing import Dict, Any

# Pattern entries: (regex, ats_name, is_legacy, notes)
# Add new patterns at the bottom. Order matters only when patterns might
# overlap, more specific ones first.
ATS_PATTERNS = [
    (r"greenhouse\.io", "Greenhouse", False, "Modern, robust keyword extraction"),
    (r"ashbyhq\.com", "Ashby", False, "Modern parser, handles complex resumes well"),
    (r"lever\.co", "Lever", False, "Modern, robust"),
    (r"\.wd\d+\.myworkdayjobs\.com|\.workdayjobs\.com", "Workday", False, "Auto-fills application form from resume"),
    (r"smartrecruiters\.com", "SmartRecruiters", False, "Modern parser"),
    (r"\.icims\.com|icims\.com", "iCIMS", True, "Older versions strict, treat all iCIMS as legacy for fail-unsafe"),
    (r"taleo\.net", "Taleo", True, "Legacy parser, always conservative"),
    (r"\.fa\.(us\d+|eu\d+|em\d+|ca\d+)\.oraclecloud\.com", "Oracle Fusion HCM", False, "Modern Oracle Cloud HCM"),
    (r"amazon\.jobs", "Amazon ATS", False, "Internal proprietary system"),
    (r"jobs\.careers\.microsoft\.com|careers\.microsoft\.com", "Microsoft (Workday based)", False, "Workday based"),
    (r"linkedin\.com/jobs/view", "LinkedIn Easy Apply", False, "LinkedIn pulls profile data directly, resume supplementary"),
    (r"jobvite\.com", "Jobvite", False, "Solid modern parser"),
    (r"ats\.rippling\.com|rippling\.com/recruiting", "Rippling", False, "Modern"),
    (r"bamboohr\.com", "BambooHR", False, "Smaller employers typically"),
    (r"apply\.workable\.com", "Workable", False, "Modern"),
    (r"applytojob\.com", "JazzHR", True, "Older, treat as legacy for fail-unsafe"),
    (r"twilio\.com/careers|jobs\.twilio\.com", "Twilio (custom)", False, "Custom careers portal, modern"),
    (r"careers\.snowflake\.com", "Snowflake (custom)", False, "Custom careers portal"),
    (r"careers\.cognizant\.com", "Cognizant (custom)", False, "Custom careers portal"),
    (r"accenture\.com/.*careers", "Accenture (custom)", False, "Custom careers portal"),
    (r"careers\.oracle\.com", "Oracle Recruiting (modern)", False, "Modern Oracle careers portal"),
    (r"careers\.mastercard\.com", "Mastercard Workday", False, "Workday based"),
    (r"corporate\.visa\.com/en/jobs", "Visa Workday", False, "Workday based"),
    (r"careers\.fisglobal\.com|careers\.fiserv\.com", "FIS/Fiserv (custom)", False, "Custom careers portal"),
    (r"jobs\.globalpayments\.com", "Global Payments (custom)", False, "Custom careers portal"),
    (r"careers\.spglobal\.com", "S&P Global (custom)", False, "Custom careers portal"),
    (r"jobs\.adp\.com", "ADP (custom)", False, "Custom careers portal"),
    (r"careers\.equifax\.com", "Equifax (custom)", False, "Custom careers portal"),
    (r"careers\.veeva\.com", "Veeva (custom)", False, "Custom careers portal"),
    (r"jobs\.iqvia\.com", "IQVIA (custom)", False, "Custom careers portal"),
    (r"careers\.epam\.com|epam\.com/careers", "EPAM (custom)", False, "Custom careers portal"),
    (r"careers\.dxc\.com", "DXC (custom)", False, "Custom careers portal"),
    (r"careers\.cisco\.com|jobs\.cisco\.com", "Cisco (custom)", False, "Custom careers portal"),
    (r"www\.cdwjobs\.com", "CDW (custom)", False, "Custom careers portal"),
    (r"careers\.datadoghq\.com", "Datadog (Greenhouse based)", False, "Greenhouse based"),
    (r"theladders\.com", "Ladders (recruiter)", True, "Recruiter posting, treat as conservative for unknown destination"),
]


def detect_ats(url: str) -> Dict[str, Any]:
    """Detect ATS from URL. Returns dict with ats, is_legacy, use_conservative_render, notes."""
    if not url:
        return {
            "ats": "Unknown",
            "is_legacy": False,
            "use_conservative_render": True,
            "notes": "No URL provided, conservative render applied per fail-unsafe rule",
        }
    for pattern, name, is_legacy, notes in ATS_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return {
                "ats": name,
                "is_legacy": is_legacy,
                "use_conservative_render": is_legacy,
                "notes": notes,
            }
    return {
        "ats": "Unknown",
        "is_legacy": False,
        "use_conservative_render": True,
        "notes": "Unknown ATS, conservative render applied per fail-unsafe rule",
    }


def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: ats_detector.py <url>\n")
        return 2
    info = detect_ats(sys.argv[1])
    print(json.dumps(info, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
