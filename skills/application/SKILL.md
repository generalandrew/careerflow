---
name: careerflow-application
description: Triggered when the user wants to apply to a specific job posting. Handles the full per-application flow, ingests posting URL or pasted JD text, detects ATS, generates tailored resume + posting summary + talking points, places everything in a dated application folder, updates the spreadsheet tracker. Use when the user pastes a job URL, says "apply to this", "tailor a resume for", "this job", or similar. Also handles status updates ("applied", "rejected", "interviewing", "offer", "accepted", "declined", "closed"), interview prep generation ("build interview prep for X"), cover letter generation ("generate a cover letter for X"), and callback lookup ("callback from X").
---

# careerflow application skill

You are processing a job application for the user. Read this entire skill before starting.

## When this skill triggers

- User pastes a URL that looks like a job posting
- User says "apply to this [URL]" or "tailor a resume for [Company]" or similar
- User pastes raw JD text and says "apply to this"
- User says a status update word ("applied", "rejected", "interviewing", "offer received", "accepted", "declined", "closed")
- User says "build interview prep for [Company]" or "prep me for [Company]"
- User says "generate a cover letter for [Company]"
- User says "callback from [Company]" or "who is [Company]"

## The per-application flow

### Step 1, Create the application folder

Today's date in `YYYY-MM-DD` format. Folder name pattern: `YYYY-MM-DD_<CompanySlug>_<RoleSlug>` where slugs strip non-alphanumeric and cap at 40 chars. Place under `applications/`.

If you can't determine company or role from the URL/JD, ask the user.

### Step 2, Ingest the posting

Try URL fetch first:

```bash
python3 scripts/apply.py --url "<URL>" --company "<Company>" --role "<Role>"
```

If the fetch returns HTTP error (403, 404, 500), most job boards block scrapers. Fall back to asking the user to paste the JD text:

> The site blocked the scrape. Please paste the full job description text in your next message and I'll continue.

After paste:

```bash
echo "<pasted text>" | python3 scripts/ingest_posting.py --paste applications/<folder> \
    --title "<role>" --company "<company>" --url-override "<URL>"
```

### Step 3, ATS detection

The `apply.py` orchestrator calls `ats_detector.py` automatically and writes the detected ATS into `posting.json`. Surface the ATS in chat:

> ATS detected: <name> | conservative render: <true/false>

If `use_conservative_render = true`, you'll pass `--conservative` to build_resume.js in step 5.

### Step 4, Tailor the resume

Read `master/experience.json`, `posting.json`, and any prior `tailored.json` (if this is a re-tailor). Build a new `tailored.json` for this specific posting.

**JD vocabulary rule.** Aim for 40% more JD-specific vocabulary in Experience bullets than the source brand language from prior employers. Mirror exact phrasing from the JD (e.g., if the JD says "deal shaping" use "deal shaping", not "pursuit shaping"; if the JD says "PoV" use "PoV", not "PoC"). The keyword density score checker `scripts/ats_keyword_score.py` can validate this.

**SAP Single-Title Rule (or equivalent).** Roles with promotions inside the same company should be a single entry under the latest title with the full date span. Do not use `tenures[]` sub-arrays.

**NDA rule.** Never write a protected customer name. Anonymize as "a global shipping and logistics customer" or "a professional sports franchise" or "a Fortune 50 banking customer". Run `python3 scripts/nda_audit.py applications/<folder>` after tailoring to verify.

**Honest gap acknowledgment.** When fit is a stretch, do not overclaim. State the gap honestly in the posting summary and the resume positioning.

Write `applications/<folder>/tailored.json`.

### Step 5, Render

```bash
python3 scripts/apply.py --tailored applications/<folder>/tailored.json
```

This calls `build_resume.js` with the right `--conservative` flag based on the ATS detection from step 3.

Output lands at `applications/<folder>/<Name>_Resume_<Company>.docx`.

### Step 6, Write the posting summary

Generate company_summary, responsibilities_concise (5-8 bullets), match_snapshot (honest fit assessment including gaps), and talking_points. Pipe a JSON payload to write_summary.py:

```bash
echo '<JSON payload>' | python3 scripts/write_summary.py
```

This writes `posting_summary.md` and updates `applications.xlsx` with the row.

### Step 7, Automated checks (run all unless user opts out)

Three checks run after rendering, in order:

**a. NDA audit**

```bash
python3 scripts/nda_audit.py applications/<folder>
```

If any customer names are flagged, anonymize them in tailored.json and re-render before continuing.

**b. ATS keyword density score**

```bash
python3 scripts/ats_keyword_score.py applications/<folder>
```

If score is below 30%, revise tailored.json to weave more JD vocabulary into bullets, re-render. If score is 30 to 50%, surface the result but proceed.

**c. Salary band reality check**

```bash
python3 scripts/salary_band_check.py \
    --role "<posting role>" \
    --company "<posting company>" \
    --level "<seniority from targeting>" \
    --market "<posting location or user metro>"
```

Compare the band against:
- The posted compensation (if present in posting.json)
- The user's `compensation_targets.base_min` and `base_max` from experience.json

Surface:
- If posted comp is below user's base_min, flag "under-priced for your targets"
- If posted comp is above user's base_max, flag "over your stated ceiling, stretch role"
- If no comp posted, surface the defensible range as negotiation anchor

The user can skip any check by saying "skip NDA audit", "skip keyword score", or "skip salary check" before this step.

### Step 8, Present to the user

Reply with:
- Link to the resume DOCX
- Link to the posting summary
- Honest 1-paragraph fit assessment surfaced from the match_snapshot
- ATS detected
- Compensation if found
- Any honest gaps flagged
- "Submit via [URL] and say 'applied' when done."

## Status updates

When the user says one of these words, update `metadata.json` and the matching row in `applications.xlsx`:

- "applied" → status = "Applied", date_applied = today, last_touch = today
- "rejected" or "closed" → status = "Rejected", last_touch = today, add `closed_date` to metadata
- "interviewing" → status = "Interviewing", last_touch = today
- "offer received" → status = "Offer", last_touch = today
- "accepted" → status = "Accepted", last_touch = today
- "declined" → status = "Declined", last_touch = today
- "outreach" (for cold emails) → status = "Outreach", last_touch = today

If the user doesn't specify which company, ask. If only one application is in `Draft` status, default to that one and confirm.

## Interview prep generation

When the user says "build interview prep for [Company]":

1. Find the application folder.
2. Read posting.json, posting_summary.md, tailored.json.
3. Build a comprehensive interview prep JSON payload with:
   - background (recent context on company)
   - questions (likely questions with rationale and talking points)
   - questions_to_ask_them (intelligent reverse questions)
   - star_stories (relevant STAR stories from interview_anecdotes.md)
   - red_flag_handling (how to gracefully handle expected gaps)
   - close_script (strong closing statement)
4. Pipe to write_interview_prep.py:
   ```bash
   echo '<JSON>' | python3 scripts/write_interview_prep.py
   ```

## Cover letter generation

When the user says "generate a cover letter for [Company]":

1. Find the application folder.
2. Read posting.json and tailored.json.
3. Build a cover letter JSON payload (see `scripts/write_cover_letter.py` docstring for schema).
4. Use 3 paragraphs:
   - Opening, hook + why this company specifically
   - Body, 1-2 paragraphs with concrete past achievement that maps to the role
   - Closing, specific ask + next step
5. Pipe to write_cover_letter.py:
   ```bash
   echo '<JSON>' | python3 scripts/write_cover_letter.py
   ```

## Callback lookup

When the user says "callback from [Company]" or "who is [Company]":

1. Search `applications.xlsx` for matching Company.
2. If multiple matches, list them and ask which one.
3. Read the matching application folder's posting_summary.md, tailored.json, interview_prep.md (if exists).
4. Surface:
   - Role title and date applied
   - Posting summary (key responsibilities + match snapshot)
   - Talking points
   - Recent status notes from metadata.json

## Cold outreach mode

When the user says "cold outreach to [Company]" or "introduce me to [Company]":

1. Create folder with suffix `_GeneralizedColdOutreach`.
2. Generate a generalized tailored.json from `master/experience.json` (broader positioning, no specific JD).
3. Render the resume.
4. Generate a cold email draft based on the user's recent themes.
5. Add row to applications.xlsx with status = "Outreach".

## Discovery scans

careerflow ships 17 optional discovery scans. See `docs/scan_index.md` for the complete catalog and trigger phrases.

All scans:
- Read `master/experience.json -> targeting` and filter results by the user's profile
- Dedupe against `applications.xlsx`
- Output to `candidates_v<N>_<scan_name>.md` in the workspace root, where N is the next integer after the highest existing `candidates_v*` file
- Include the targeting profile used at the top of the output for reproducibility

If the targeting profile is empty when a scan is triggered, surface a warning and ask the user to populate it first via the onboarding flow.

When the user says any trigger phrase from `docs/scan_index.md`, load the corresponding `docs/<scan_name>_runtime.md` and follow its procedure.

## Updating the targeting profile

When the user says "update my targeting" or equivalent:

1. Read current `master/experience.json -> targeting`.
2. Ask which fields to revise (target_job_types, target_seniority_levels, excludes, industries, geographic, compensation).
3. Update the file and confirm.
4. Note that next discovery scan will use the new targeting.

## Reminders

- Always use today's date for new folders, derive from `date +%Y-%m-%d` via bash, never assume.
- Always dedupe new applications against `applications.xlsx` before creating a folder.
- Always run the NDA audit before presenting the resume to the user.
- Always foreground honest gaps in the match_snapshot. Overclaiming kills credibility.
