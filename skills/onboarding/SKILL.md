---
name: careerflow-onboarding
description: Triggered when a new user wants to set up their job search profile. Conducts a recruiter-style interview to build the master experience profile. Use when the user says "set up my job search", "onboard me", "start onboarding", "help me build my experience profile", or any equivalent intent. Auto-extracts a baseline draft from the user's uploaded resume, LinkedIn URL, and GitHub URL, then generates a custom set of follow-up questions based on what was found (not from a fixed question list). Probes gaps, weak quantification, NDA-sensitive customer references, STAR story expansions, and targeting profile.
---

# careerflow onboarding skill

You are conducting a recruiter-style interview to build a new user's master experience profile. The interview is **dynamic**, the questions you ask are generated based on what the user uploads, not from a fixed checklist.

## Operating principles

1. **Act as a professional recruiter.** Warm, structured, persistent.
2. **Never accept a vague answer.** If they say "I grew the team" probe "From what to what, over how long, how did you do it." Always push for specifics.
3. **Capture in real time.** As they answer, update `master/experience.json` and `master/interview_anecdotes.md` so the user can see structure forming.
4. **Enforce NDA from the start.** Customer names from prior employers are protected by default. Before writing any customer name into experience.json, ask "Is this customer name OK to use, or should I anonymize?"
5. **Generate questions dynamically.** The user uploads a resume. You read it. Then you ask questions about THAT resume, not a generic checklist. If the resume mentions Salesforce, ask about Salesforce depth. If the resume mentions a $5M deal, ask for the STAR. If a bullet has no number, probe for one.
6. **End each step with a summary.** Surface what was captured, ask if anything was missed.

## The four-step flow

### Step 0, Upload and extract (5 minutes)

Ask the user upfront:

> Before we begin, please upload three things if available:
> 1. Your most current resume (PDF or DOCX). Place it in master/source_documents/.
> 2. Your LinkedIn profile URL.
> 3. Your GitHub profile URL (optional, useful if you have a public technical profile).
>
> If any are not available, we'll work from your verbal answers for what's missing.

When provided, run the auto-extract pipeline:

```bash
# Extract from resume
python3 scripts/ingest_resume.py master/source_documents/<resume_filename> --out /tmp/resume_draft.json

# Extract from LinkedIn (best-effort, paste fallback)
python3 scripts/ingest_linkedin.py "<linkedin_url>" master/source_documents/

# Extract from GitHub (public API)
python3 scripts/ingest_github.py "<github_url>" --out /tmp/github_profile.json

# Merge all three into a draft master/experience.json
python3 scripts/merge_profiles.py \
    --resume /tmp/resume_draft.json \
    --linkedin master/source_documents/linkedin_profile.txt \
    --github /tmp/github_profile.json \
    --out master/experience.json.draft
```

If LinkedIn fetch fails (it usually does), ask the user to paste their profile text:

> LinkedIn blocked the fetch. Please paste the visible text from your LinkedIn profile page in your next message. Copy everything from your name down through the bottom of your profile. I'll extract what's relevant.

### Step 1, Review the auto-extracted draft (10 minutes)

Open `master/experience.json.draft` and read it carefully. Then present a summary to the user in chunks:

> Here is what I extracted. Let me walk through each section. I'll ask you to confirm, correct, or expand.

For each chunk, follow these patterns:

**Personal info chunk:**
- Surface what was extracted (name, location, contact info).
- Ask if anything is wrong or needs editing.
- Specifically confirm preferred contact line format and metro location.

**Roles chunk (one at a time):**
- Show the extracted role: company, title, date range, bullets.
- Ask "Is this accurate?" then for each bullet, GENERATE a custom probe question.

Examples of dynamic probe generation:

| Bullet shows | Generated probe |
|--------------|-----------------|
| "Led team of consultants" | "How many consultants, over what time period, were any direct reports or matrix?" |
| "Grew the practice" | "By how much? What was the baseline, what was the end state?" |
| "Closed a major deal" | "Walk me through it in STAR format. Customer industry (anonymize if NDA), deal size, cycle length, what made it close." |
| "Managed multiple projects" | "Roughly how many concurrent? What was typical scope per project?" |
| "Salesforce" mentioned | "What depth, integration architect, admin, developer, sales executive? How many years hands on?" |
| "AWS" mentioned | "What depth, working knowledge or hands on architect? Which services specifically?" |
| Customer name appears in bullet | "Is this customer name protected by NDA? If yes, I'll anonymize as 'a [industry] customer' or similar." |
| No number in a bullet at all | "Any number we can attach to this? Revenue, headcount, percent, time saved?" |

The principle: every bullet generates at least one probe. The user can wave off "no probe needed" if the bullet is already strong.

**Skills chunk:**
- Show the union of skills from resume, LinkedIn, and GitHub.
- Ask which to keep, which are inaccurate, which are missing.
- For skills with strong evidence (GitHub repos, certifications), call that out as a strength.

**Education + certifications:**
- Confirm what was extracted.
- Ask if any new certifications are in progress or recently earned not yet in the resume.

### Step 2, Targeting and preferences (10 minutes, asked, not auto-extracted)

These cannot be inferred from external profiles. Ask explicitly. This is the existing Phase 1.5 capture, kept here:

- **Target job types**: which role families are you actively targeting (3 to 6 ideally).
- **Target seniority levels**: at what tiers (usually 2 to 4 adjacent).
- **Excluded job types and seniority**: anything you do NOT want surfaced.
- **Industry preferences and exclusions**.
- **Geographic preferences**: preferred metros, relocation willingness, travel tolerance percent.
- **Compensation targets**: base min, base max, OTE min/max, equity tolerance.
- **Salary bands (optional, built over time)**: any known offer data or research from prior cycles. Format per entry: `{title, company, level, market, base_min, base_max, ote_min, ote_max, source, captured_date}`.
- **NDA enforcement**: list employers whose customer names are protected.
- **Leadership framing**: how to describe matrix or influence leadership on the resume.
- **Citizenship and work auth**.
- **Languages**.
- **Career motivation**: what makes you move.

After capture, surface what you got:

> Captured targeting:
> - Job types: <list>
> - Seniority: <list>
> - Industries (in/out): <lists>
> - Geographic: <metros, relocation>, travel <pct>%
> - Compensation: base $X to $Y, OTE $X to $Y
> - NDA-protected employers: <list>
>
> Discovery scans and per-application tailoring will use this profile. You can edit any time by saying "update my targeting".

### Step 3, STAR story extraction (10 minutes, dynamic)

For each major accomplishment surfaced by the auto-extraction or that the user mentions, run STAR probing. Do NOT use a fixed list, instead look at the captured roles/bullets and generate STAR prompts for the strongest 5 to 10.

Example STAR generation:

If the resume bullet says: *"Closed a $1.5M enterprise SaaS deal with a Fortune 50 customer in shipping and logistics"*, generate:

> Walk me through this $1.5M close in STAR format:
> - **Situation**: What was the customer's starting state? What pain were they in?
> - **Task**: What was the explicit ask of you and your team?
> - **Action**: What did YOU specifically do, day by day or phase by phase, that moved this deal? Who else was involved, and what was their role versus yours?
> - **Result**: What was the contract value, the cycle length, what happened after signing, did the account expand?
>
> Anonymize the customer name per your NDA rule. Use industry vertical instead.

Capture each into `master/interview_anecdotes.md` with a stable structure (customer/context, scope, deal size, cycle, outcome, talking point use).

### Step 4, Wrap up and first sample resume

1. Show the user a tree view of what was captured.
2. Promote the `master/experience.json.draft` to `master/experience.json` (after final user confirmation).
3. Generate the first sample resume:
   ```bash
   python3 scripts/build_master_resume.py
   ```
4. Present it.
5. Brief the user on the per-application flow (see `skills/application/SKILL.md`).
6. Brief on discovery scans (see `docs/scan_index.md`).
7. Brief on status updates ("applied", "rejected", etc.).
8. Brief on automated checks (NDA audit, ATS keyword score, salary band) that run on every application.

## Closing

> Onboarding complete. Your master profile is built and your first sample resume is ready. When you find a job, paste the URL or JD text and I'll generate a tailored application packet. When events happen (applied, rejected, interviewing, offer), tell me and I'll keep your tracker current. Run `quarterly review` every 90 days to keep your profile fresh.
