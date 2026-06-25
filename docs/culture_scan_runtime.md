# Glassdoor Culture-Fit Scan Runtime

Optional layered scan that takes a candidate list already surfaced by other scans and layers Glassdoor review data (rating, recent culture trend, manager quality, work-life balance) to re-rank.

## Trigger phrases

- `run culture scan on candidates_v<N>`
- `score culture fit for [company]`
- `add culture data to [candidates file]`

## Inputs

- An existing `candidates_v<N>.md` file (output of another scan).
- Optional, user culture priorities (e.g., "I value work-life balance above pay", "I prioritize strong engineering culture").

## Procedure

1. Load the candidates list from the source file.
2. For each company, fan out WebSearch calls against:
   - `glassdoor.com` for overall rating, CEO approval, recent reviews
   - `levels.fyi` for compensation reality check (signals if pay floor is competitive)
   - `teamblind.com` for anonymous current-employee sentiment
3. Capture per company:
   - Glassdoor overall rating (X / 5)
   - 12-month rating trend (improving / flat / declining)
   - Top 3 themes from recent positive reviews
   - Top 3 themes from recent negative reviews
   - Manager quality score if available
4. Re-rank the candidate list adding a "Culture Fit Score" column and reordering Tier 1/2/3.
5. Output to `candidates_v<N>_culture_scored.md` (preserves original, adds suffix).

## Notes

- Glassdoor reviews are noisy. Take broad sentiment, not individual reviews, as the signal.
- A 3.5+ rating with improving trend is healthy. Below 3.0 or declining trend is a yellow flag worth investigating.
- Recommended cadence: run on each new candidate batch before applying.
