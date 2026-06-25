# Pipeline Digest Runtime

Automated runtime that generates a digest of pipeline status: applications submitted this week, status changes, applications needing followup, interviews pending, active offers, and recent discovery scan output. Designed for daily or weekly review.

## Trigger phrases

- `pipeline digest`
- `weekly digest`
- `show my pipeline`
- `give me a status update`

## Procedure

1. Read `applications.xlsx`.
2. Bucket applications by:
   - Submitted in the last N days (default 7)
   - Status changes in the last N days
   - Stale Applied status (last touch > M days, default 7)
   - Currently Interviewing
   - Active Offers
3. Find the 3 most recent `candidates_v*.md` files in the workspace root.
4. Compose a Markdown digest with sections for each bucket.
5. Recommend next actions at the bottom (e.g., "run followup scan", "build interview prep").
6. Write to `digest_<YYYY-MM-DD>.md` in the workspace root.

## CLI usage

```bash
python3 scripts/pipeline_digest.py [--days 7] [--followup-threshold 7] [--out custom_name.md]
```

## Recommended cadence

- Daily for active job search (Monday morning ritual is ideal)
- Weekly for passive/exploratory mode
- Tie to the `scheduled-tasks` MCP for automated generation

## Scheduling via Cowork scheduled tasks

```
Create scheduled task:
  Cron: 0 8 * * MON
  Prompt: "Generate this week's pipeline digest by running `python3 scripts/pipeline_digest.py`. Surface the digest content in chat, highlight active offers, interviews, and stale applications needing followup."
```

## Output sections

The digest includes:
- Summary counts
- Active Offers (highest priority)
- Currently Interviewing
- Applications Needing Followup (sorted by age)
- Status Changes (last N days)
- New Submissions (last N days)
- Recent Discovery Scans (links to top 3)
- Recommended Actions
