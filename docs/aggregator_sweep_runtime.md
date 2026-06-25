# Job Board Aggregator Sweep Runtime

Optional discovery runtime that pulls the user's targeting profile against job board aggregators. Lower precision than careers-page scans, but broader coverage for surfacing roles at companies not on the named lists.

## Trigger phrases

- `run aggregator sweep`
- `scan job boards`
- `run wellfound built in scan`

## Inputs

- User targeting profile from `master/experience.json -> targeting`.
- Pipeline dedupe source: `applications.xlsx` Company column.
- Geographic preferences from `preferences.geographic_constraints`.

## Procedure

1. Build aggregator search queries from `target_job_types` + `target_seniority_levels` + geographic preferences.
2. Fan out parallel WebSearch calls against:
   - `indeed.com`
   - `builtin.com`
   - `wellfound.com` (formerly AngelList Talent)
   - `otta.com`
   - `remoteok.com`
   - `weworkremotely.com`
   - `dice.com`
3. For each result, extract the company name, role title, location, and apply URL.
4. Dedupe against `applications.xlsx` and against the other results in this run.
5. Score and tier against the targeting profile.
6. Compile into `candidates_v<N>_aggregator_sweep.md`.

## Notes

- Aggregator data quality varies. Verify each role on the source careers page before applying.
- Indeed and Built In tend to surface mid-market roles, Wellfound and Otta lean toward Series A-C startups.
- Recommended cadence: weekly.
