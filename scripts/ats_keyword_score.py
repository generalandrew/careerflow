#!/usr/bin/env python3
"""
ats_keyword_score.py - Score a tailored.json against a posting.json by
counting matched JD vocabulary terms across the resume body.

Outputs:
  - Total terms tracked
  - Terms matched in Summary
  - Terms matched in Core Competencies
  - Terms matched in Experience bullets
  - Terms matched in Skills
  - Overall density score (0-100)
  - Missing high-priority terms (in JD but not in resume)

Usage:
    python3 scripts/ats_keyword_score.py <app_dir>
    # or
    python3 scripts/ats_keyword_score.py <tailored.json> <posting.json>
"""
import argparse, json, re, sys
from pathlib import Path
from collections import Counter


def tokenize(text):
    """Lowercase, alphanumeric word tokens. Keeps multi-word phrases intact in caller."""
    return re.findall(r"\b[a-z][a-z0-9\-\+\/]*\b", text.lower())


def extract_jd_terms(posting):
    """Pull candidate keyword terms from posting.json.

    Sources, in priority order:
      1. posting.keywords (already extracted by ingest_posting.py)
      2. Top single words from raw_text by frequency, excluding stopwords
      3. Multi-word capitalized phrases from raw_text (proper nouns / titles)
    """
    terms = set()
    for k in posting.get("keywords", []):
        terms.add(k.lower())

    text = posting.get("raw_text", "")
    if text:
        STOPWORDS = set("""a about above after again against all am an and any are as at be because been before being
            below between both but by could did do does doing don down during each few for from further had has have
            having he her here hers herself him himself his how i if in into is it its itself just me more most my
            myself no nor not now of off on once only or other our ours ourselves out over own re s same she should so
            some such t than that the their theirs them themselves then there these they this those through to too
            under until up very was we were what when where which while who whom why will with would you your yours
            yourself yourselves can may might must shall ought
            this we are also our""".split())
        tokens = tokenize(text)
        counter = Counter(t for t in tokens if t not in STOPWORDS and len(t) > 2)
        # Top 30 most frequent (skip the first 5 which are usually common JD framing terms)
        for word, count in counter.most_common(50):
            if count >= 2:
                terms.add(word)

    return sorted(terms)


def resume_section_text(tailored, section):
    """Extract text from a section of tailored.json."""
    if section == "summary":
        return tailored.get("summary", "")
    if section == "core_competencies":
        return " ".join(tailored.get("core_competencies", []))
    if section == "experience":
        bits = []
        for r in tailored.get("roles", []):
            bits.append(r.get("title", ""))
            bits.append(r.get("scope", ""))
            for b in r.get("bullets", []):
                bits.append(b if isinstance(b, str) else b.get("text", ""))
        return " ".join(bits)
    if section == "skills":
        bits = []
        skills = tailored.get("skills", {})
        if isinstance(skills, dict):
            for cat, items in skills.items():
                bits.append(cat)
                bits.extend(items)
        elif isinstance(skills, list):
            bits.extend(skills)
        return " ".join(bits)
    return ""


def score_term_in_section(term, section_text):
    return bool(re.search(rf"\b{re.escape(term)}\b", section_text, re.IGNORECASE))


def score(tailored, posting):
    terms = extract_jd_terms(posting)
    sections = ["summary", "core_competencies", "experience", "skills"]
    section_text = {s: resume_section_text(tailored, s) for s in sections}

    matches = {s: [] for s in sections}
    matched_any = set()
    for term in terms:
        for s in sections:
            if score_term_in_section(term, section_text[s]):
                matches[s].append(term)
                matched_any.add(term)

    overall_pct = 100 * len(matched_any) / max(len(terms), 1)
    missing = [t for t in terms if t not in matched_any]

    return {
        "terms_total": len(terms),
        "terms_matched": len(matched_any),
        "overall_density_pct": round(overall_pct, 1),
        "by_section": {s: len(set(matches[s])) for s in sections},
        "missing_terms": missing[:30],  # top 30 missing
        "all_jd_terms": terms,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path1", help="app_dir, or tailored.json path if path2 given")
    ap.add_argument("path2", nargs="?", help="posting.json path (optional)")
    args = ap.parse_args()

    p1 = Path(args.path1).resolve()
    if p1.is_dir():
        tailored = json.loads((p1 / "tailored.json").read_text())
        posting = json.loads((p1 / "posting.json").read_text())
    else:
        tailored = json.loads(p1.read_text())
        if not args.path2:
            sys.stderr.write("Provide posting.json as second arg when first is a file\n"); return 2
        posting = json.loads(Path(args.path2).read_text())

    result = score(tailored, posting)
    print(json.dumps(result, indent=2))

    # Quick verdict
    if result["overall_density_pct"] >= 50:
        print(f"\nVERDICT: GOOD ({result['overall_density_pct']}% density)")
    elif result["overall_density_pct"] >= 30:
        print(f"\nVERDICT: ACCEPTABLE ({result['overall_density_pct']}% density), consider weaving more JD vocabulary into bullets")
    else:
        print(f"\nVERDICT: LOW ({result['overall_density_pct']}% density), tailored.json should be revised to mirror JD vocabulary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
