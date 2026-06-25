# LinkedIn Saved Search Sync Runtime

Optional discovery runtime that pulls the user's LinkedIn saved searches and job alerts into the careerflow candidate format.

## Trigger phrases

- `sync LinkedIn searches`
- `pull LinkedIn job alerts`
- `import LinkedIn saved searches`

## Inputs

- User-supplied LinkedIn saved search URL or pasted job alert email content.
- User targeting profile from `master/experience.json -> targeting` for re-filtering.
- Pipeline dedupe source: `applications.xlsx` Company column.

## Procedure

1. Ask the user to either:
   - Paste a LinkedIn saved search URL, or
   - Paste the text of a recent LinkedIn job alert email
2. If URL provided, try `python3 scripts/ingest_linkedin.py <url> /tmp/linkedin_search_out/`. LinkedIn often blocks; if it fails, ask for paste.
3. Extract role listings from the paste or fetch output: company, title, location, posted date, apply URL.
4. Dedupe against `applications.xlsx`.
5. Re-score each role against `target_job_types` + `target_seniority_levels`. Drop roles that don't match.
6. Compile into `candidates_v<N>_linkedin_sync.md`.

## Notes

- LinkedIn limits scraping aggressively. Paste-fallback is the normal path.
- Recommend the user set up 3 to 5 saved searches with explicit role-type + seniority + remote filters for highest signal.
- Recommended cadence: weekly, often paired with the weekly LinkedIn job alert email.
