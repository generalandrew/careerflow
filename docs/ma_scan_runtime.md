# Acquisition / Merger Scan Runtime

Optional discovery runtime that surfaces companies that acquired another company in the last 12 months. Integration phases typically open Solutions, Customer Engineering, and Professional Services roles to handle migration, retention, and cross-sell motions.

## Trigger phrases

- `run M&A scan`
- `scan acquisitions`
- `find post-merger hiring`

## Inputs

- Lookback window, default last 12 months.
- User targeting profile from `master/experience.json -> targeting`.
- Pipeline dedupe source: `applications.xlsx` Company column.

## Procedure

1. Fan out WebSearch calls against:
   - `crunchbase.com` M&A filter
   - `techcrunch.com` acquisition coverage
   - `bloomberg.com`, `reuters.com` deal news
   - Company press release pages
2. Capture for each deal: acquirer, target, deal value, announcement date, sector.
3. Filter to acquirer companies in industries in scope per user's targeting profile.
4. For each acquirer company, run a careers page scan for openings matching the targeting profile.
5. Compile into `candidates_v<N>_ma_picks.md` with the acquisition context surfaced alongside each opening.

## Notes

- Look for repeated acquirers (private equity portfolios, serial acquirers) as a separate signal of hiring scale.
- Cross-sell and customer success roles are often the first to open after an acquisition.
- Recommended cadence: monthly.
