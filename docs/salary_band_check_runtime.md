# Salary Band Reality Check Runtime

Research tool that pulls Levels.fyi, Built In comp, Glassdoor salary data, and the user's locally stored salary band history for a given role + company + level. Output is a defensible salary range to anchor on during negotiation.

## Trigger phrases

- `check salary band for [role] at [company]`
- `salary band for [role]`
- `comp check [company] [role]`

## Inputs

- Role title (required)
- Company name (optional, broader research if omitted)
- Level / seniority (optional, defaults to user's target_seniority_levels)
- Geographic market (optional, defaults to user's preferred metro)
- Locally stored bands from `master/experience.json -> preferences -> salary_bands -> entries[]`

## Procedure

1. Load locally stored bands from `master/experience.json`. Filter to matching title + level + market. These are the highest signal because they're real datapoints the user collected.
2. Fan out WebSearch calls against:
   - `levels.fyi` (best for software / tech roles)
   - `builtin.com` salary data
   - `glassdoor.com` company salary pages
   - `payscale.com`
   - `salary.com`
3. Capture base, OTE, equity, sign-on by source.
4. Compute aggregate range:
   - Floor: lowest defensible value across sources
   - Median: midpoint of credible sources
   - Ceiling: highest defensible value, used as anchor for negotiation
5. Surface in chat:
   - The aggregate range
   - The per-source breakdown
   - Any user-stored bands that match
   - A recommended anchor based on the user's `preferences.compensation_targets` plus the market data
6. If a flag is set, write the result to a file:
   - `--save` writes to `master/preferences/salary_research/<role>_<company>_<date>.md`
   - `--add-to-bands` appends a new entry to `experience.json -> preferences -> salary_bands -> entries[]`

## CLI usage

```bash
python3 scripts/salary_band_check.py \
    --role "Senior Solutions Engineer" \
    --company "Acme" \
    --level "Senior" \
    --market "Dallas, TX" \
    [--save] \
    [--add-to-bands]
```

## Notes

- Levels.fyi has best coverage for FAANG and top-tier tech, weaker for mid-market and non-tech.
- Glassdoor data is older and noisier but covers more companies.
- The user's locally stored bands grow over time, becoming the most accurate reference. Encourage capture after every offer or research session.
- Recommended cadence: before every application and during every offer negotiation.
