# careerflow Changelog

## v0.1.0 (Initial release, 2026-06-25)

First public release. Packaged from a working private workflow that was used to drive 60+ real job applications.

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
- Onboarding skill, recruiter-style interview across seven phases (`skills/onboarding/SKILL.md`)
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
