# Recruiter / Executive Search Firm Scan Runtime

Optional discovery runtime that surfaces executive recruiters and search firms specializing in the user's target job types + seniority. Output is a list of recruiters to reach out to (cold email or LinkedIn message). Different output type than role-listing scans.

## Trigger phrases

- `run recruiter scan`
- `find recruiters for me`
- `scan executive search firms`

## Inputs

- User targeting profile from `master/experience.json -> targeting`.
- Geographic preferences from `preferences.geographic_constraints`.

## Procedure

1. Build search queries from `target_job_types` + `target_seniority_levels` + geography. Example: "executive recruiter Solutions Engineer Director Dallas TX".
2. Fan out WebSearch calls against:
   - LinkedIn recruiter profile searches
   - Heidrick.com, kornferry.com, russellreynolds.com (top tier exec search)
   - Riviera Partners (tech leadership)
   - True Search (tech and growth)
   - Daversa Partners (startup exec)
   - Boutique technical recruiting firms in the user's metro
3. For each recruiter surfaced, capture: name, firm, LinkedIn URL, areas of focus, recent placements signal if available.
4. Compile into `candidates_v<N>_recruiters.md`.

## Output format

Different from the role-listing scans. Each entry is a recruiter contact:

- Name
- Firm
- LinkedIn URL
- Focus areas (e.g., "Series B/C SaaS GTM leadership")
- Geographic coverage
- Recommended outreach approach (LinkedIn DM, cold email via firm website, intro request)
- Talking points for the outreach message

## Notes

- Recruiter relationships are long-cycle. Even if no immediate fit, get on their list.
- Tailor the outreach message to the recruiter's stated focus, not generic.
- Recommended cadence: quarterly.
