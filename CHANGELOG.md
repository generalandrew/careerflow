# careerflow Changelog

## v0.3.0 (2026-06-25)

### Added
- **Email inbox status sync** (`scripts/email_status_sync.py`, `docs/email_status_sync_runtime.md`). IMAP-based, reads emails for application receipt confirmations, rejection notices, interview invitations, and offers. Auto-updates `metadata.json` + `applications.xlsx`. Requires user-managed config at `~/.careerflow_email_config.json`.
- **Pipeline digest** (`scripts/pipeline_digest.py`, `docs/pipeline_digest_runtime.md`). Generates weekly/daily summary of submissions, status changes, stale applications needing followup, interviews pending, active offers, and recent scan output.
- **Skill gap analysis** (`scripts/skill_gap_analysis.py`, `docs/skill_gap_analysis_runtime.md`). Reads outcomes across all applications to surface patterns: rejection rate per target family, recurring missing keywords in rejected postings, recurring matched keywords in callback postings.
- **Quarterly career review** (`scripts/quarterly_career_review.py`, `docs/quarterly_career_review_runtime.md`). Three-mode tool: `--mode prompt` generates 10 review questions, `--mode snapshot` locks the quarter's experience.json, `--mode diff` shows what was added since last snapshot.
- **Dynamic onboarding interview**. Resume parser (`scripts/ingest_resume.py`), GitHub profile fetcher (`scripts/ingest_github.py`), and profile merger (`scripts/merge_profiles.py`). The onboarding skill now auto-extracts a draft profile from uploaded resume + LinkedIn + GitHub, then generates **custom probe questions per bullet** instead of asking from a fixed list.

### Changed
- Onboarding skill rewritten to use a four-step flow: Step 0 upload + auto-extract, Step 1 dynamic review with custom probes per bullet, Step 2 targeting + preferences + salary bands, Step 3 STAR story extraction.
- Personal info scrubbed from all repo files. The repo ships with template placeholders only; user data lives only in the workspace (gitignored).

## v0.2.0 (2026-06-25)

### Added
- Targeting profile in `experience.json -> targeting`: target_job_types, target_seniority_levels, exclude_job_types, exclude_seniority_levels, industry_preferences, industry_exclusions. Drives discovery scans and per-application tailoring weights.
- Local salary band storage in `experience.json -> preferences -> salary_bands -> entries[]`, populated over time by user research and offers.
- `scripts/salary_band_check.py` for local lookup + persistence of new bands.
- 15 new discovery scan runtime docs covering: layoff comeback, IPO/S-1, aggregator sweep, LinkedIn sync, stealth, recruiter, earnings hiring signal, conference/event, M&A, PE portfolio, geographic metro, culture fit, salary band check, followup nudge, alumni network.
- `docs/scan_index.md` complete catalog with quick-reference table.
- Onboarding Phase 1.5 (Targeting) captures job type, seniority, geography, compensation, and any known salary bands before the career arc interview.
- Automated checks during each application: NDA audit, ATS keyword density score, salary band reality check. All can be skipped per application.

### Changed
- Discovery scans (S&P 500, funding round) now read targeting profile and filter results accordingly.

## v0.1.0 (Initial release, 2026-06-25)

First public release. Packaged from a working private workflow.

### Included
- End to end application orchestrator (`scripts/apply.py`)
- Posting ingester with URL fetch + paste fallback (`scripts/ingest_posting.py`)
- ATS detector with 36 URL patterns and fail-unsafe conservative render trigger (`scripts/ats_detector.py`)
- DOCX resume renderer with v1.1 ATS-friendly sanitizer (`scripts/build_resume.js`)
- Posting summary writer (`scripts/write_summary.py`)
- Interview prep brief writer (`scripts/write_interview_prep.py`)
- Cover letter generator (`scripts/write_cover_letter.py`)
- Master resume builder (`scripts/build_master_resume.py`)
- ATS keyword density score checker (`scripts/ats_keyword_score.py`)
- NDA / privacy audit tool (`scripts/nda_audit.py`)
- LinkedIn profile ingester for onboarding (`scripts/ingest_linkedin.py`)
- Workspace init script (`scripts/init_workspace.py`)
- Onboarding skill, recruiter-style interview (`skills/onboarding/SKILL.md`)
- Application skill, per-application flow (`skills/application/SKILL.md`)
- Application workflow runbook (`docs/workflow.md`)
- ATS optimization rules and per-ATS playbook (`docs/ats_optimization_rules.md`)
- S&P 500 short list scan runtime (`docs/sp500_scan_runtime.md`)
- Series B/C funding round scan runtime (`docs/funding_round_scan_runtime.md`)
- Empty templates for `master/` files
- Setup scripts for Mac, Linux, Windows
- GPL v3 LICENSE

### Known limitations
- LinkedIn ingester relies on user pasting profile text when public scraping fails
- ATS detector covers the most common 36 platforms; rare or custom ATSs default to fail-unsafe conservative render
- Discovery scans require internet access from the Claude session
- No Cowork plugin packaging yet (future release)
