# Public Company Earnings + Hiring Signal Scan Runtime

Optional discovery runtime that reads recent earnings call transcripts for hiring signals (e.g., "we're investing in customer engineering", "expanding professional services") and matches them to open roles on the company careers page.

## Trigger phrases

- `run earnings scan`
- `scan earnings hiring signals`
- `find companies investing in [function]`

## Inputs

- User targeting profile from `master/experience.json -> targeting`.
- Sector preferences from `targeting.industry_preferences`.
- Pipeline dedupe source: `applications.xlsx` Company column.

## Procedure

1. Build search queries for recent quarterly earnings call transcripts in the user's industries. Example: "Q4 2026 earnings call transcript investing professional services SaaS".
2. Fan out WebSearch calls against:
   - `seekingalpha.com`
   - `fool.com` (Motley Fool transcripts)
   - Company investor relations pages
   - `marketwatch.com`
   - `motley-fool-stock-advisor.com`
3. For each transcript surfaced, search for hiring-related phrases that map to user `target_job_types`. Examples to look for:
   - "investing in [function]"
   - "expanding our [function] team"
   - "hiring across [function]"
   - "scaling our [function] organization"
   - "professional services growth"
   - "customer engineering build out"
4. For each company with a positive hiring signal, scan the careers page for matching open roles.
5. Compile into `candidates_v<N>_earnings_signal.md` with the earnings quote alongside each opening.

## Notes

- Highest signal scan when the user's target_job_type aligns with an executive's stated investment focus.
- Recommended cadence: quarterly, aligned to earnings season (mid-Jan, mid-Apr, mid-Jul, mid-Oct).
- Include the earnings call quote alongside each candidate as a talking point for the application.
