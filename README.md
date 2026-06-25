# careerflow

An AI-driven job application workflow. Built to run inside Claude (Cowork mode or Claude Code) on the user's local machine.

careerflow turns job searching into a structured, repeatable practice. You bring your career story. Claude builds your master experience profile through a guided recruiter-style interview. Then for every job posting you paste, Claude generates a tailored ATS-optimized resume, a posting summary with talking points, and an application packet that is automatically tracked in a spreadsheet.

## What it does

- Onboards you with a recruiter-style interview that builds your master experience profile (one time, 30 to 60 minutes)
- Generates a tailored DOCX resume for every job posting you paste, ATS-optimized
- Detects the target Applicant Tracking System from the URL and applies the right render variant (fail-unsafe)
- Writes a per-application posting summary, match snapshot, and talking points
- Optionally generates an interview prep brief in STAR format
- Optionally generates a cover letter
- Optionally runs discovery scans for the S&P 500 short list or Series B/C funding round companies
- Tracks all applications in a spreadsheet with status (Draft, Applied, Interviewing, Rejected, Offer, Accepted, Declined)
- Provides callback lookup, when a recruiter calls, surfaces the right packet instantly
- Enforces customer-name NDA protection from prior employers by default

## Requirements

- Python 3.9 or newer
- Node.js 18 or newer
- A workspace folder on your computer (the setup script creates one)
- Claude Code, or Cowork mode in the Claude desktop app, with file access to the workspace folder
- Two Python packages, `openpyxl` for the application tracker and `requests` is optional for some helpers
- One Node package, `docx` for resume generation

## Quick start

### 1. Clone this repo

```bash
git clone git@github.com:generalandrew/careerflow.git ~/careerflow
cd ~/careerflow
```

### 2. Run setup

On Mac or Linux:

```bash
bash setup.sh
```

On Windows:

```bat
setup.bat
```

The setup script creates a workspace folder at `~/Documents/careerflow-workspace/` (or your chosen path), copies all the scripts, installs Python and Node dependencies, and scaffolds the empty template files for your master experience profile.

### 3. Connect Claude to the workspace

Open Claude Code or Cowork mode. Tell Claude to access your workspace folder. The exact step depends on which tool you use:

- **Cowork mode**, click the folder icon, navigate to `~/Documents/careerflow-workspace/`, and approve access.
- **Claude Code**, run Claude Code from inside the workspace folder, `cd ~/Documents/careerflow-workspace && claude`.

### 4. Trigger onboarding

Tell Claude:

> set up my job search

Claude reads the onboarding skill (`skills/onboarding/SKILL.md`) and acts as a professional recruiter. It interviews you about your career across seven phases. Have your most recent resume ready to upload, and your LinkedIn profile URL handy.

By the end of onboarding, your `master/experience.json` is populated, your `master/interview_anecdotes.md` story bank has 5 to 10 STAR-format anchor stories, and Claude has generated your first sample resume.

### 5. Apply to a job

Paste a job posting URL into Claude:

> apply to this job, https://example.com/careers/job/12345

Claude:

1. Creates a dated application folder
2. Ingests the posting (URL fetch, falls back to asking for paste if blocked)
3. Detects the ATS and chooses the right render variant
4. Generates the tailored DOCX resume with 40 percent more JD vocabulary in your Experience bullets
5. Writes a posting summary with match snapshot and talking points
6. Updates your `applications.xlsx` tracker

When you submit, tell Claude `applied` and the tracker updates.

### 6. Optional, generate interview prep or cover letter

> build interview prep for Company

> generate a cover letter for Company

### 7. Optional, run a discovery scan

careerflow ships 17 optional discovery scans, all triggered by chat phrases. Examples:

- `run S&P 500 scan` — surface S&P 500 roles matching your targeting
- `run funding round scan` — Series B/C growth-stage roles
- `run layoff scan` — companies rebounding from layoffs
- `run IPO scan` — post-IPO and S-1 filing companies
- `run aggregator sweep` — Indeed, Built In, Wellfound roles
- `sync LinkedIn searches` — pull your LinkedIn saved searches
- `run stealth scan` — stealth startups with notable founders
- `run recruiter scan` — executive recruiters to engage
- `run earnings scan` — companies with positive hiring signals in earnings calls
- `run event scan` — sponsors at upcoming industry conferences
- `run M&A scan` — acquirer companies in last 12 months
- `run PE portfolio scan` — companies in major PE firm portfolios
- `run [metro] scan` — all scans filtered to one geographic metro
- `run culture scan on candidates_v<N>` — re-rank by Glassdoor data
- `check salary band for [role] at [company]` — defensible salary range
- `run followup scan` — applications needing followup
- `scan alumni network` — warm intros from school + employer overlaps

See `docs/scan_index.md` for the complete catalog.

Outputs a ranked candidate list in the workspace root.

## Repository structure

```
careerflow/
├── README.md
├── LICENSE                                # GPL v3
├── CHANGELOG.md
├── setup.sh                               # Mac/Linux installer
├── setup.bat                              # Windows installer
├── docs/
│   ├── workflow.md                        # The runbook Claude follows
│   ├── ats_optimization_rules.md          # Content + format + per-ATS playbook
│   ├── scan_index.md                      # Catalog of all 17 discovery scans
│   ├── sp500_scan_runtime.md              # S&P 500 short list scan
│   ├── funding_round_scan_runtime.md      # Series B/C funding round scan
│   ├── layoff_scan_runtime.md             # Layoff comeback scan
│   ├── ipo_scan_runtime.md                # IPO / S-1 scan
│   ├── aggregator_sweep_runtime.md        # Job board aggregator sweep
│   ├── linkedin_sync_runtime.md           # LinkedIn saved search sync
│   ├── stealth_scan_runtime.md            # Stealth / pre-launch scan
│   ├── recruiter_scan_runtime.md          # Executive search firm scan
│   ├── earnings_scan_runtime.md           # Earnings call hiring signal scan
│   ├── event_scan_runtime.md              # Conference / event scan
│   ├── ma_scan_runtime.md                 # Acquisition / merger scan
│   ├── pe_portfolio_scan_runtime.md       # PE-backed portfolio scan
│   ├── metro_scan_runtime.md              # Geographic metro deep dive
│   ├── culture_scan_runtime.md            # Glassdoor culture-fit scan
│   ├── salary_band_check_runtime.md       # Salary band research
│   ├── followup_scan_runtime.md           # Followup nudge scan
│   └── alumni_scan_runtime.md             # Alumni network scan
├── scripts/
│   ├── apply.py                           # End to end packet orchestrator
│   ├── ingest_posting.py                  # URL fetch or paste, structured posting.json
│   ├── ats_detector.py                    # URL to ATS detection, fail-unsafe conservative
│   ├── build_resume.js                    # DOCX renderer, sanitizer, conservative variant
│   ├── build_master_resume.py             # Render full master resume from experience.json
│   ├── write_summary.py                   # Posting summary writer + xlsx updater
│   ├── write_interview_prep.py            # STAR format interview prep brief
│   ├── write_cover_letter.py              # Cover letter generator
│   ├── ats_keyword_score.py               # JD vocabulary density score checker
│   ├── nda_audit.py                       # Customer name privacy audit
│   ├── salary_band_check.py               # Local salary band lookup + research persistence
│   ├── ingest_linkedin.py                 # LinkedIn URL ingester for onboarding
│   └── init_workspace.py                  # Workspace scaffold script (called by setup)
├── skills/
│   ├── onboarding/SKILL.md                # Recruiter interview flow
│   └── application/SKILL.md               # Per-application flow
└── templates/
    ├── master/
    │   ├── experience.json.template
    │   ├── interview_anecdotes.md.template
    │   ├── assessments.md.template
    │   └── references.md.template
    └── applications.xlsx.template          # generated by init_workspace.py
```

## What runs where

- `scripts/` are scripts run by Python or Node, callable by Claude during the workflow.
- `skills/` are markdown documents Claude reads when triggered, no code.
- `docs/` are reference documents Claude consults during decision points (ATS rules, runbooks).
- `templates/` are starter files copied to the user's workspace during setup.

## What is and is not in this repo

In the repo:
- All scripts, skills, docs, templates
- LICENSE (GPL v3)
- Setup scripts for Mac, Linux, and Windows

Not in the repo (kept private on your machine via .gitignore):
- Your `master/experience.json` populated with your career data
- Your `master/interview_anecdotes.md` story bank
- Your `master/assessments.md` containing PI Behavioral Score IDs etc
- Your `applications.xlsx` with your real applications
- Your `applications/` folders with per-application packets
- Your generated resumes (`*.docx`)
- Your candidates_v\*.md discovery scan outputs

## Customization

After onboarding, edit any of these to customize:

- `docs/workflow.md`, the runbook Claude follows. Add your own rules or constraints.
- `docs/ats_optimization_rules.md`, the ATS playbook. Add new ATS patterns as you encounter them.
- `scripts/ats_detector.py`, add new URL patterns for ATSs not yet covered.
- `scripts/build_resume.js`, change fonts, colors, layout, sanitizer rules.

## Privacy and NDA

careerflow enforces a default rule that customer names from your prior employers are not written to your experience profile or to any generated resume without your explicit confirmation. During onboarding, Claude asks which employers' customer relationships are under NDA.

## Contributing

Pull requests welcome. Please open an issue first to discuss substantive changes. Code is GPL v3, contributions must be compatible.

## Privacy

careerflow stores all personal data locally in the user's workspace folder. Nothing in this repository contains user-specific information. The user's master profile, applications, generated resumes, and discovery scan results live only on the user's machine and are excluded from version control by `.gitignore`.

## License

GPL v3. See LICENSE for the full text.
