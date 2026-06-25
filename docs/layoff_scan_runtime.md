# Recent Layoff Comeback Scan Runtime

Optional discovery runtime that surfaces companies that did public layoffs in the last 6 to 12 months and are now actively hiring again. These companies often have eager hiring teams and a more pragmatic bar because they are refilling specific functional gaps.

## Trigger phrases

- `run layoff scan`
- `run layoff comeback`
- `scan layoff rebound`

## Inputs

- Lookback window, default last 6 to 12 months. Adjust by editing this file.
- User targeting profile from `master/experience.json -> targeting`.
- Pipeline dedupe source: `applications.xlsx` Company column.
- Industry preferences and exclusions from `targeting`.

## Procedure

1. Fan out WebSearch calls against `layoffs.fyi`, `techcrunch.com`, `bloomberg.com`, `reuters.com` for company names with public layoff news in the lookback window.
2. Filter to industries in scope per the user's targeting profile.
3. Dedupe against `applications.xlsx`.
4. For each remaining company, run a targeted WebSearch against its careers domain looking for openings matching `target_job_types` + `target_seniority_levels`.
5. Score each surfaced role:
   - Include only if title matches at least one target_job_type AND one target_seniority_level
   - Drop if title contains any exclude_*
6. Compile results into `candidates_v<N>_layoff_comeback.md`.
7. Group into Tier 1 (direct fit), Tier 2 (strong fit), Tier 3 (watch list).
8. Report in chat reply with the targeting profile used.

## Notes

- Include date of layoff in each candidate entry, so the user can judge how long ago the cut happened.
- Flag if the layoff was concentrated in a function adjacent to the user's target role (red flag for stability).
- Recommended cadence: monthly.
