#!/usr/bin/env python3
"""
ingest_posting.py
Fetch a job posting URL, save raw HTML snapshot, and produce a structured
posting.json. Falls back to manual paste mode when the site blocks.

Usage:
    python3 scripts/ingest_posting.py <url> <output_dir>
        [--title "..."] [--company "..."] [--url-override "..."]
    python3 scripts/ingest_posting.py --paste <output_dir>
        [--title "..."] [--company "..."] [--url-override "..."]

Outputs (in output_dir):
    posting.html   raw HTML snapshot (or pasted text)
    posting.json   { url, fetched_at, title, company, location, raw_text,
                     keywords, meta, compensation }
"""
import sys, os, json, re, argparse, datetime, urllib.request, urllib.error

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
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&#39;", "'", text)
    text = re.sub(r"&quot;", '"', text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_meta(html):
    out = {}
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if m:
        out["page_title"] = re.sub(r"\s+", " ", m.group(1)).strip()
    for prop, key in [("og:title", "og_title"), ("og:site_name", "og_site_name")]:
        m = re.search(rf'<meta[^>]+property=["\']?{prop}["\']?[^>]+content=["\'](.*?)["\']', html, re.IGNORECASE)
        if m:
            out[key] = m.group(1).strip()
    return out


# Hints used for lightweight keyword extraction. Users can edit this list to
# reflect their domain (Andrew's defaults skew technical solutions / consulting).
KEYWORD_HINTS = [
    "director","manager","principal","senior","lead","head","vp","vice president","architect","consultant","engineer",
    "solution","solutions","pre-sales","presales","delivery","implementation","architecture","strategy",
    "saas","cloud","aws","azure","gcp","api","microservices","integration","kubernetes","docker","python","javascript","sql","ai","ml","llm","data",
    "commerce","composable","mach","cms","crm","cdp","customer data","martech","marketing","personalization","analytics",
    "sap","salesforce","adobe","sitecore","contentful","commercetools","shopify","optimizely",
    "agile","scrum","devops","ci/cd","sow","rfp","rfi","jira","confluence",
    "supply chain","retail","manufacturing","logistics","healthcare","finance","fintech",
]


def keyword_match(text):
    low = text.lower()
    found = []
    for k in KEYWORD_HINTS:
        if re.search(rf"\b{re.escape(k)}\b", low):
            found.append(k)
    return sorted(set(found))


def extract_compensation(text):
    """Best-effort regex extraction of salary range and benefits."""
    comp = {"salary_min": None, "salary_max": None, "currency": None,
            "bonus_or_commission": False, "equity": False, "benefits": [],
            "raw_match": None, "notes": ""}

    patterns = [
        r"\$\s?(\d{2,3}(?:,\d{3})?(?:\.\d+)?)\s*(?:K|k)?\s*[\-–—to]+\s*\$?\s?(\d{2,3}(?:,\d{3})?(?:\.\d+)?)\s*(?:K|k)?",
        r"(\d{2,3},\d{3})\s*[\-–—to]+\s*(\d{2,3},\d{3})",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            def to_num(s):
                s = s.replace(",", "")
                return int(float(s)) if "." in s or s.isdigit() else None
            lo, hi = to_num(m.group(1)), to_num(m.group(2))
            if lo and hi and lo < 10000:
                lo, hi = lo * 1000, hi * 1000
            comp["salary_min"] = lo
            comp["salary_max"] = hi
            comp["currency"] = "USD" if "$" in m.group(0) or "USD" in text[max(0, m.start()-20):m.end()+20] else None
            comp["raw_match"] = m.group(0).strip()
            break

    if re.search(r"\b(bonus(?:es)?|commissions?|incentives?|variable\s+pay)\b", text, re.IGNORECASE):
        comp["bonus_or_commission"] = True
    if re.search(r"\b(equity|RSUs?|stock\s+options?|stock\s+grants?)\b", text, re.IGNORECASE):
        comp["equity"] = True

    benefit_keywords = {
        "Medical/Dental/Vision": r"\b(medical|dental|vision)\b",
        "401K": r"\b401\s?\(?k\)?\b",
        "PTO/Flexible Time Off": r"\b(PTO|paid time off|flexible time off|vacation)\b",
        "Parental Leave": r"\b(parental leave|maternity|paternity)\b",
        "Remote": r"\bremote\b",
        "Hybrid": r"\bhybrid\b",
        "Wellness": r"\b(wellness|fitness|gym)\b",
        "Pet Insurance": r"\bpet\s?insurance\b",
    }
    for label, pat in benefit_keywords.items():
        if re.search(pat, text, re.IGNORECASE):
            comp["benefits"].append(label)

    return comp


def parse(url, html, title_override=None, company_override=None):
    text = strip_html(html) if "<" in html else html
    meta = extract_meta(html) if "<" in html else {}
    title = title_override or meta.get("og_title") or meta.get("page_title") or ""
    company = company_override or meta.get("og_site_name") or ""

    loc = ""
    m = re.search(r"\b(Remote|Hybrid|On-?site)\b[^.]{0,80}?\b([A-Z][a-z]+(?:,\s*[A-Z]{2})?)", text)
    if m:
        loc = m.group(0).strip()

    return {
        "url": url,
        "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
        "title": title,
        "company": company,
        "location": loc,
        "raw_text": text[:60000],
        "keywords": keyword_match(text),
        "compensation": extract_compensation(text),
        "meta": meta,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="URL to fetch, or output_dir if --paste")
    ap.add_argument("output_dir", nargs="?")
    ap.add_argument("--paste", action="store_true", help="Read posting text from stdin")
    ap.add_argument("--title", default=None)
    ap.add_argument("--company", default=None)
    ap.add_argument("--url-override", dest="url_override", default=None)
    args = ap.parse_args()

    if args.paste:
        out_dir = args.input
        url = args.url_override
        sys.stderr.write("Paste posting text. End with Ctrl-D:\n")
        html = sys.stdin.read()
    else:
        url = args.input
        out_dir = args.output_dir
        if not out_dir:
            sys.stderr.write("output_dir required\n"); return 2
        try:
            html = fetch(url)
        except urllib.error.HTTPError as e:
            sys.stderr.write(f"HTTP {e.code} on {url}. Re-run with --paste {out_dir}\n")
            return 3
        except Exception as e:
            sys.stderr.write(f"Fetch failed: {e}. Re-run with --paste {out_dir}\n")
            return 3

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "posting.html"), "w", encoding="utf-8") as f:
        f.write(html)

    posting = parse(url, html, title_override=args.title, company_override=args.company)
    with open(os.path.join(out_dir, "posting.json"), "w", encoding="utf-8") as f:
        json.dump(posting, f, indent=2)

    sys.stdout.write(f"Saved posting.html and posting.json to {out_dir}\n")
    sys.stdout.write(f"Title: {posting['title']}\nCompany: {posting['company']}\n")
    sys.stdout.write(f"Keywords: {', '.join(posting['keywords'][:20])}\n")
    c = posting["compensation"]
    if c["salary_min"]:
        rng = f"${c['salary_min']:,} - ${c['salary_max']:,}" if c["salary_max"] else f"${c['salary_min']:,}+"
        extras = []
        if c["bonus_or_commission"]: extras.append("bonus/commission")
        if c["equity"]: extras.append("equity")
        sys.stdout.write(f"Compensation: {rng}" + (" + " + ", ".join(extras) if extras else "") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
