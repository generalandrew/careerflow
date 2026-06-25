# Geographic Metro Deep Dive Runtime

Optional discovery runtime that pulls all named-employer scans (S&P 500, funding round, layoff, IPO, M&A, PE portfolio) and filters strictly to a single geographic metro. Use when geographic constraints harden.

## Trigger phrases

- `run [metro] scan` (e.g., `run DFW scan`, `run Austin scan`, `run NYC scan`)
- `metro deep dive [metro]`
- `scan everything in [metro]`

## Inputs

- Metro to scan (passed via trigger phrase). Default: first metro from `preferences.geographic_constraints.preferred_metros`.
- All other scan inputs (targeting profile, dedupe source).

## Procedure

1. Run the union of all base scans (S&P 500, funding round, layoff, IPO, M&A, PE portfolio, aggregator sweep).
2. For each surfaced role, validate the location matches the target metro:
   - Exact match on metro name in role title or location field
   - Match on commutable cities within 50 miles
   - Honor remote-eligibility for the metro's state
3. Drop any role not matching the geographic filter.
4. Re-tier the merged list. Tier 1 entries are in-metro AND match targeting profile precisely.
5. Compile into `candidates_v<N>_<metro>_deep_dive.md`.

## Notes

- This is the heaviest scan, takes longest to run, returns the most relevant results when geo is a hard constraint.
- For DFW, valid metros include Fort Worth, Dallas, Plano, Frisco, Addison, Irving, Coppell, Las Colinas, Grapevine, Southlake, Arlington, Mansfield, Cleburne, Weatherford, Burleson, Aledo.
- For NYC, include Manhattan, Brooklyn, Jersey City, Hoboken, Long Island City, White Plains.
- Recommended cadence: when relocating, or when remote roles dry up.
