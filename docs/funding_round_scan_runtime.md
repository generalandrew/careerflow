# Series B and C Funding Round Scan Runtime

Chat-driven discovery runtime to surface live Director / Senior Manager / Principal openings at companies that recently raised a Series B or Series C round.

## Trigger phrases

- `run funding round scan`
- `scan series B C`
- `scan growth stage`

## Why Series B and C

Companies at Series B and C are in scaling mode. Product market fit, recent fresh capital, building out enterprise GTM motions. This is the stage where Solutions Architecture, Professional Services, Forward Deployed Engineering, and Customer Engineering roles open in volume. Earlier than B is pre-PMF, later than C favors known brand hires over generalist seniors.

## Inputs

- Filter band: Series B or Series C announced in the last 12 months.
- Sector filter: read from `master/experience.json -> targeting -> industry_preferences` (with `industry_exclusions` applied).
- Region filter: US headquartered or US remote eligible (or honor `preferences.geographic_constraints` for stricter geo).
- Pipeline dedupe source: `applications.xlsx` Company column.
- **User targeting profile from `master/experience.json -> targeting`**:
  - `target_job_types` and `target_seniority_levels` filter the per-company role scan
  - `exclude_job_types` and `exclude_seniority_levels` drop matches

## Procedure

1. Fan out WebSearch calls to surface a fresh universe of recent Series B and Series C announcements. Suggested seeds:
   - `Series B funding 2026 enterprise SaaS`
   - `Series C funding 2026 AI infrastructure`
   - `Series B 2026 fintech infrastructure`
   - `Series C 2026 data platform`
   - `Series B 2026 customer data platform`
   - `Series C 2026 agentic AI startup`
   - `Series B 2026 vertical SaaS`
   - allowed_domains: `techcrunch.com`, `crunchbase.com`, `pitchbook.com`, `axios.com`, `pymnts.com`, `siliconangle.com`, `bloomberg.com`.
2. Dedupe surfaced companies against sector exclude list and against `applications.xlsx`.
3. Load the user targeting profile from `master/experience.json -> targeting`. For each remaining company, run one targeted WebSearch against the company's careers domain (greenhouse.io, lever.co, ashbyhq.com, or own subdomain). Build the search query from `target_job_types` and `target_seniority_levels`. Score each result against the same filter:
   - **Include only if** the role title contains at least one of `target_job_types` AND at least one of `target_seniority_levels`.
   - **Drop if** the role title contains any of `exclude_job_types` OR any of `exclude_seniority_levels`.
4. Compile results into `candidates_v<N>_funding_round_picks.md` where N is the next integer after the highest existing `candidates_v*` file.
5. Group results into Tier 1, Tier 2, Tier 3.
6. Report total live picks surfaced, total companies scanned, and recommended apply order.

## Output schema

Same as the S&P 500 scan output. Sections:

- Title with date and funding round band
- Source line listing the seeds used
- Tier 1, Direct Fit, Apply First (5 max)
- Tier 2, Strong Fit, Apply Second Wave (5 max)
- Tier 3, Watch List (open ended)
- Companies surfaced from funding news but no Director-tier opening
- Total live picks summary
- Recommended apply order
- Sources, markdown hyperlinks to each funding announcement and JD per company

## Fit scoring rubric

Per company, score against the user's skill set as documented in `master/experience.json`. High signal patterns:

- Pre-sales SA or SE role, value based demos, executive advisory, POCs
- Professional Services leadership, SOW authorship, billable utilization
- Forward Deployed Engineering, customer facing technical leadership
- Solutions Architecture Director or Principal
- AI Adoption, AI Transformation, AI Practice lead roles
- Customer Engineering Director or Manager at infrastructure or developer tools companies

Low signal, skip:

- Individual contributor software engineer roles at any level
- Sales quota-carrying AE roles (unless user has specifically pivoted)
- Marketing, Operations, HR unrelated to GTM technical leadership

## Refresh cadence

Recommended cadence: every 2 weeks. Each run produces a new `candidates_v<N>_funding_round_picks.md` file.

## Configuration

To customize the scan, edit this file:

- Lookback window, default `last 12 months`. Adjust by editing the "Filter band" line above.
- Funding band, default `Series B or C`. Adjust by editing the band line.
- Sector seeds, edit the search seed list in step 1.

The trigger phrase always reads this file at runtime, so changes take effect immediately on the next scan.
