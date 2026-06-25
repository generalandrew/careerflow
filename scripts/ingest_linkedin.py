#!/usr/bin/env python3
"""
ingest_linkedin.py - Attempt to fetch a public LinkedIn profile page and
extract structured profile text for onboarding. Falls back to paste mode.

LinkedIn is aggressive about blocking scrapers and requires authentication
for most profile content. This script makes a best-effort fetch of public
data. When it fails (which is common), Claude should fall back to asking
the user to paste their LinkedIn profile export.

Usage:
    python3 scripts/ingest_linkedin.py <linkedin_url> <output_dir>
    python3 scripts/ingest_linkedin.py --paste <output_dir>

Outputs:
    linkedin_profile.html   raw snapshot (or pasted text)
    linkedin_profile.txt    cleaned text for Claude to read
"""
import sys, os, re, argparse, urllib.request, urllib.error
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=20) as r:
        charset = r.headers.get_content_charset() or "utf-8"
        return r.read().decode(charset, errors="replace")


def strip_html(html):
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="LinkedIn URL, or output_dir if --paste")
    ap.add_argument("output_dir", nargs="?")
    ap.add_argument("--paste", action="store_true", help="Read profile text from stdin")
    args = ap.parse_args()

    if args.paste:
        out_dir = args.input
        sys.stderr.write("Paste LinkedIn profile text. End with Ctrl-D:\n")
        raw = sys.stdin.read()
        text = raw
    else:
        url = args.input
        out_dir = args.output_dir
        if not out_dir:
            sys.stderr.write("output_dir required\n"); return 2
        try:
            raw = fetch(url)
            text = strip_html(raw)
        except urllib.error.HTTPError as e:
            sys.stderr.write(
                f"HTTP {e.code} on {url}\n"
                f"LinkedIn typically blocks automated fetches.\n"
                f"Re-run with --paste {out_dir} and paste your profile text manually.\n"
            )
            return 3
        except Exception as e:
            sys.stderr.write(
                f"Fetch failed: {e}\n"
                f"Re-run with --paste {out_dir} and paste your profile text manually.\n"
            )
            return 3

    os.makedirs(out_dir, exist_ok=True)
    (Path(out_dir) / "linkedin_profile.html").write_text(raw, encoding="utf-8")
    (Path(out_dir) / "linkedin_profile.txt").write_text(text, encoding="utf-8")
    print(f"Saved linkedin_profile.html and linkedin_profile.txt to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
