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

careerflow ships 17 optional discovery scans. See `docs/scan_index.md` for the complete catalog and quick reference table.

All scans are optional. All read the user targeting profile from `master/experience.json -> targeting` and dedupe against `applications.xlsx`. Output goes to `candidates_v<N>_<scan_name>.md` (or a scan-specific output file) in the workspace root.

The scan categories:

- **Named-employer scans**: S&P 500, funding round, layoff, IPO, M&A, PE portfolio, stealth
- **Broad surface scans**: aggregator sweep, LinkedIn sync, conference / event
- **Geographic narrowing**: metro deep dive
- **Quality re-ranking**: culture fit
- **Pipeline maintenance**: followup nudge, alumni network
- **Research and prep**: recruiter scan, earnings hiring signal, salary band check

## Automated checks during applications

When the user pastes a job URL and the application flow runs, Claude performs three automated checks after rendering the resume:

1. **NDA audit** (`scripts/nda_audit.py`). Scans the rendered DOCX, the tailored.json, and the posting_summary.md for any customer names from protected employers. If hits found, surfaces them and asks the user to anonymize before submitting.

2. **ATS keyword density score** (`scripts/ats_keyword_score.py`). Scores the tailored.json against the posting.json. Reports density percent. If below 30%, surfaces missing high-priority terms and recommends weaving more JD vocabulary into Experience bullets.

3. **Salary band reality check** (`scripts/salary_band_check.py` + `docs/salary_band_check_runtime.md`). Looks up local stored bands plus web-sourced data for the role + company + level. Reports defensible range and recommended anchor. Surfaces if posted compensation is below the user's `compensation_targets.base_min` (under-priced) or above ceiling (out-of-band reach).

All three checks run automatically. The user can disable any check by saying "skip NDA audit", "skip keyword score", or "skip salary check" before the final render.

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
