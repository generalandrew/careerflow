# Skill Gap Analysis Runtime

Reads `applications.xlsx` plus per-application `posting.json` to identify patterns: which target job-type families perform best, which keywords from rejected postings are absent from the user's profile (potential gaps), which keywords correlate with callbacks (strengths to lean into).

## Trigger phrases

- `run skill gap analysis`
- `analyze my outcomes`
- `where am I getting rejected`

## Inputs

- `applications.xlsx` with at least 10 to 20 closed applications for meaningful signal.
- `master/experience.json -> targeting` for job-type family classification.
- `master/experience.json -> skills` + `roles[].bullets` for skill blob.
- `posting.json` from each application folder for keywords.

## Procedure

1. Load all applications.
2. Bucket by status (Rejected, Interviewing, Offered, Accepted, etc.).
3. For each application, classify the role into one of the user's target_job_types or "Other".
4. Compute per-family stats: applied, rejected, interviewing, offered.
5. For rejected applications, collect posting.json keywords that do NOT appear in the user's skill blob -> potential gaps.
6. For interviewing/offered applications, collect posting.json keywords that DO appear in the user's skill blob -> strength signals.
7. Generate recommendations:
   - Worst-performing family (high rejection rate) -> consider revising positioning or de-prioritizing.
   - Best-performing family (high callback rate) -> consider doubling down.
   - Top recurring keyword gaps -> consider building hands-on experience or a certification.
8. Write `skill_gap_<YYYY-MM-DD>.md` to the workspace root.

## CLI usage

```bash
python3 scripts/skill_gap_analysis.py [--out custom_name.md]
```

## Recommended cadence

- Quarterly, after at least 20 closed applications.
- Whenever you feel the pipeline is stalling.

## Output sections

- Total volume and outcome summary
- Per Job-Type Family Stats (table)
- Potential Skill Gaps (top 20 keywords in rejected postings missing from profile)
- Strength Signal (top 20 keywords in callback postings present in profile)
- Recommendations (worst family, best family, top gap closures to consider)
