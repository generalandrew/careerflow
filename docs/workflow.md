# careerflow Workflow Runbook

The chat-driven workflow Claude follows when running careerflow for a user.

## Master files

- `master/experience.json` is the canonical source of truth for the user's career.
- `master/interview_anecdotes.md` is the anonymized STAR story bank.
- `master/assessments.md` stores assessment IDs (PI Behavioral, Hogan, DISC, etc.).
- `master/references.md` stores reference contacts (optional).
- `master/source_documents/` holds the user's original resume PDF/DOCX and LinkedIn export.

These are populated during onboarding (see `skills/onboarding/SKILL.md`) and maintained over time as the user's career evolves.

## Per-application files

For each job posting the user applies to, careerflow creates `applications/<YYYY-MM-DD>_<Company>_<Role>/` with:

| File | Purpose |
|------|---------|
| `posting.html` | Raw scrape or pasted JD text |
| `posting.json` | Structured posting (title, company, location, raw_text, keywords, compensation, ats) |
| `posting_summary.md` | Company summary, responsibilities concise, match snapshot, talking points |
| `tailored.json` | The tailored content used to render the resume |
| `<Name>_Resume_<Company>.docx` | The final ATS-optimized resume |
| `interview_prep.md` | (optional) STAR-format interview prep brief |
| `CoverLetter_<Company>.docx` | (optional) cover letter |
| `metadata.json` | Status, dates, contacts, notes |

## ATS optimization

See `docs/ats_optimization_rules.md` for the full content and format playbook plus per-ATS quirks.

The renderer (`scripts/build_resume.js`) produces ATS-clean DOCX with v1.1 sanitizer:
- Date ranges with dashes preserved (`Mar 2021 - Apr 2023`)
- `Email:` / `Phone:` / `LinkedIn:` labels preserved
- Other dashes, colons, semicolons normalized to natural language

The detector (`scripts/ats_detector.py`) maps URLs to ATS names and applies the fail-unsafe rule: if `is_legacy == true` OR `ats == "Unknown"`, the renderer is invoked with `--conservative` flag (disables decorative borders, collapses Core Competencies to single column, uses black text).

## JD Vocabulary Match Rule

When authoring `tailored.json`, target **40 percent more JD-specific vocabulary in Experience bullets** than baseline. JD vocabulary means the exact terminology, phrasing, and word choice used in the target Job Description (for example, "deal shaping" vs "pursuit shaping", "PoV" vs "PoC", "agentic AI" vs "GenAI", "trusted advisor" vs "strategic partner"). Use `scripts/ats_keyword_score.py` to validate.

## NDA Rule

Customer names from prior employers are protected by default. Before writing any customer name into a tailored.json or experience.json, anonymize as "a Fortune 50 banking customer" or "a global shipping and logistics customer" or "a professional sports franchise" or similar. Run `scripts/nda_audit.py` on every application folder before presenting the resume.

The user's protected employer list is captured during onboarding in `experience.json -> nda_rule` and `experience.json -> protected_employers`.

## Status workflow

Application states tracked in `applications.xlsx -> Status`:

- `Draft` - folder created, not yet submitted
- `Applied` - submitted, awaiting response
- `Interviewing` - in active interview process
- `Offer` - offer received
- `Accepted` - offer accepted
- `Declined` - offer declined
- `Rejected` - rejected by employer or closed
- `Outreach` - cold outreach with no posted opening

The user signals state transitions in chat ("applied", "rejected", etc.) and Claude updates `metadata.json` and the matching xlsx row.

## Callback lookup

When a recruiter calls, the user says `callback from [Company]`. Claude searches `applications.xlsx` for matching Company rows, opens the application folder, and surfaces the posting summary, talking points, and interview prep brief (if present).

## Discovery scans

Two optional discovery workflows ship with careerflow:

### S&P 500 short list scan

Trigger phrases: `run S&P 500 scan`, `run sp500 scan`, `scan the short list`.

See `docs/sp500_scan_runtime.md` for the procedure. Output goes to `candidates_v<N>_sp500_picks.md`.

### Series B/C funding round scan

Trigger phrases: `run funding round scan`, `scan series B C`, `scan growth stage`.

See `docs/funding_round_scan_runtime.md` for the procedure. Output goes to `candidates_v<N>_funding_round_picks.md`.

## Scripts reference

| Path | Purpose |
|------|---------|
| `scripts/apply.py` | End to end packet orchestrator, also handles render-only mode |
| `scripts/ingest_posting.py` | URL fetch or paste, structured posting.json |
| `scripts/ats_detector.py` | URL -> ATS mapping, fail-unsafe conservative flag |
| `scripts/build_resume.js` | DOCX renderer, v1.1 sanitizer, conservative variant |
| `scripts/write_summary.py` | posting_summary.md + xlsx updater |
| `scripts/write_interview_prep.py` | STAR-format interview prep brief |
| `scripts/write_cover_letter.py` | Cover letter DOCX |
| `scripts/build_master_resume.py` | Full master resume from experience.json |
| `scripts/ats_keyword_score.py` | JD vocabulary density score check |
| `scripts/nda_audit.py` | Customer name leak detector |
| `scripts/ingest_linkedin.py` | LinkedIn profile ingester (best effort, paste fallback) |
| `scripts/init_workspace.py` | Generate empty applications.xlsx with canonical schema |
