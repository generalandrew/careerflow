#!/usr/bin/env python3
"""
ingest_github.py - Fetch a public GitHub profile and extract signals: top
languages, pinned repos, top repos by stars, recent activity, bio.

Uses the GitHub public API (no auth required, but rate limited to 60
req/hour without a token). Optional GITHUB_TOKEN env var raises the limit
to 5000 req/hour.

Usage:
    python3 scripts/ingest_github.py <github_url_or_username> [--out github_profile.json]
"""
import argparse
import collections
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path


def parse_username(s):
    m = re.search(r"github\.com/([\w\-]+)", s, re.IGNORECASE)
    if m:
        return m.group(1)
    return s.strip().lstrip("@")


def gh_get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "careerflow",
        "Accept": "application/vnd.github+json",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"GitHub API HTTP {e.code} on {url}\n")
        return None
    except Exception as e:
        sys.stderr.write(f"GitHub API fetch failed: {e}\n")
        return None


def fetch_profile(username):
    user = gh_get(f"https://api.github.com/users/{username}")
    if not user:
        return None
    # All repos (paginated, fetch up to 100)
    repos = gh_get(f"https://api.github.com/users/{username}/repos?per_page=100&sort=stars&direction=desc")
    repos = repos or []
    # Languages aggregated
    lang_counter = collections.Counter()
    for r in repos:
        if r.get("language"):
            lang_counter[r["language"]] += 1
    # Top 10 by stars
    top_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:10]
    # Pinned: GitHub doesn't expose pinned via REST API; fall back to top by stars
    return {
        "username": username,
        "name": user.get("name"),
        "bio": user.get("bio"),
        "location": user.get("location"),
        "company": user.get("company"),
        "public_repos": user.get("public_repos"),
        "followers": user.get("followers"),
        "languages_aggregate": dict(lang_counter.most_common(15)),
        "top_repos_by_stars": [
            {
                "name": r.get("name"),
                "description": r.get("description"),
                "stars": r.get("stargazers_count", 0),
                "language": r.get("language"),
                "url": r.get("html_url"),
                "updated_at": r.get("updated_at"),
            }
            for r in top_repos
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="GitHub profile URL or username")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    username = parse_username(args.input)
    profile = fetch_profile(username)
    if not profile:
        return 3

    out_json = json.dumps(profile, indent=2)
    if args.out:
        Path(args.out).write_text(out_json)
        print(f"Wrote {args.out}")
    else:
        print(out_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
