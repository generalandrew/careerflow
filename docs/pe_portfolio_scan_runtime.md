# PE-Backed Portfolio Scan Runtime

Optional discovery runtime that surfaces companies in private equity portfolios with active hiring. PE-backed companies tend to professionalize GTM and ops quickly post-acquisition, which opens Solutions, Customer Engineering, and PS leadership roles.

## Trigger phrases

- `run PE portfolio scan`
- `scan private equity portfolios`
- `scan PE-backed companies`

## Inputs

- User targeting profile from `master/experience.json -> targeting`.
- Pipeline dedupe source: `applications.xlsx` Company column.

## Procedure

1. Fan out WebSearch calls against major PE firm portfolio pages:
   - Vista Equity Partners
   - Thoma Bravo
   - KKR
   - Blackstone
   - Silver Lake
   - Bain Capital Tech
   - TPG Capital
   - Hellman and Friedman
   - Insight Partners (later stage growth equity)
   - General Atlantic
   - Roe Strategic Capital (and other mid-market PE)
2. Extract the portfolio company list per firm.
3. Filter to companies in industries in scope per user's targeting profile.
4. Dedupe against `applications.xlsx`.
5. For each portfolio company, run a careers page scan for openings matching the targeting profile.
6. Compile into `candidates_v<N>_pe_portfolio.md` grouped by PE sponsor (so the user can see thematic plays).

## Notes

- Annotate each entry with the PE sponsor for context. The sponsor often signals investment thesis (e.g., Vista focuses on enterprise software, Thoma on cybersecurity).
- Newly acquired portfolio companies (last 12 months) are higher signal than mature holds.
- Recommended cadence: quarterly.
