# Stealth / Pre-Launch Scan Runtime

Optional discovery runtime that surfaces stealth or pre-launch companies with notable founders (ex-Big Tech, ex-known startup leaders) hiring early teams. Highest risk, highest reward.

## Trigger phrases

- `run stealth scan`
- `scan pre-launch`
- `scan founder stage`

## Inputs

- User targeting profile from `master/experience.json -> targeting`.
- Pipeline dedupe source: `applications.xlsx` Company column.

## Procedure

1. Fan out WebSearch calls against:
   - Twitter/X founder announcement search ("ex-Google launching", "ex-OpenAI building", "ex-Stripe stealth")
   - `crunchbase.com` stealth-stage filter
   - `wellfound.com` early-stage filter
   - TechCrunch and SiliconANGLE "stealth" articles
2. Surface companies with founders from notable employers in the user's industry preferences.
3. Score each based on founder pedigree, funding signal, and apparent role fit.
4. For each surfaced company, attempt to find an open role (often direct outreach to founder is the path, not a careers page).
5. Compile into `candidates_v<N>_stealth_picks.md`.

## Notes

- Stealth companies often have no careers page. Direct founder outreach via LinkedIn or Twitter is the primary application path.
- Flag founder LinkedIn URLs in the output for warm outreach.
- Recommended cadence: monthly. Lower signal-to-noise than other scans, but high payoff when it hits.
