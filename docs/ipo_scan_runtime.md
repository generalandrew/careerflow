# IPO / S-1 Filing Scan Runtime

Optional discovery runtime that surfaces companies that filed an S-1 or had a recent IPO. Post-IPO companies hire aggressively to scale GTM, customer engineering, and enterprise infrastructure.

## Trigger phrases

- `run IPO scan`
- `run S-1 scan`
- `scan post IPO`

## Inputs

- Lookback window, default last 18 months for IPOs and last 6 months for S-1 filings (S-1 implies IPO is imminent, hiring is already in flight).
- User targeting profile from `master/experience.json -> targeting`.
- Pipeline dedupe source: `applications.xlsx` Company column.

## Procedure

1. Fan out WebSearch calls for "S-1 filing 2026", "IPO 2026 [sector]", "recent IPO [user industry preferences]" against `sec.gov`, `techcrunch.com`, `bloomberg.com`, `marketwatch.com`, `cnbc.com`.
2. Filter to industries in scope per the user's targeting profile.
3. Dedupe against `applications.xlsx`.
4. For each company, run a targeted WebSearch against its careers domain looking for openings matching `target_job_types` + `target_seniority_levels`.
5. Score and group same as the S&P 500 scan.
6. Compile into `candidates_v<N>_ipo_picks.md`.

## Notes

- Annotate each company with IPO date or S-1 file date.
- Note IPO valuation if known, signals scale of GTM investment.
- Recommended cadence: monthly.
