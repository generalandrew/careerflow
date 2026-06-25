# Followup Nudge Scan Runtime

Optional runtime that reads `applications.xlsx`, finds applications applied 7+ days ago with no status change, and generates a followup email draft per row for the user to send.

## Trigger phrases

- `run followup scan`
- `find applications needing followup`
- `who should I follow up with`

## Inputs

- `applications.xlsx` rows.
- Default age threshold: 7 days since `Last Touch` with status still `Applied`.
- Optional override age threshold via the trigger phrase, e.g., `followup scan 14 days`.

## Procedure

1. Load `applications.xlsx`. Filter to rows where:
   - Status == `Applied`
   - Last Touch date is more than N days ago (default 7)
2. For each matching row, load the matching application folder's `posting_summary.md`, `tailored.json`, `metadata.json` for context.
3. Generate a followup email draft per row, using:
   - Recipient: contact name from metadata.json if present, otherwise "Hiring Manager"
   - Tone: warm, brief, recapping interest and adding one new data point
   - Length: 3 short paragraphs max
   - Subject: "Following up on my application, [Role Title]"
4. Compile into `followup_drafts_<YYYY-MM-DD>.md` in the workspace root, with one draft per row.
5. Surface in chat: count of applications needing followup, sorted by age, with first 3 drafts inline.

## Notes

- Default cadence: weekly.
- After sending each followup, the user updates that row by saying "followed up on [Company]" and Claude updates the Last Touch date.
- If a row has been followed up twice with no response, suggest moving to status `Stale` or `Withdrawn`.
