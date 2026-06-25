# Quarterly Career Review Runtime

Prompts the user to update `master/experience.json` with new wins, mentees promoted, new skills, public artifacts, and leadership changes since the last review. Without this prompt, profiles atrophy and the tailored resumes become stale.

Outputs a diff at the end of each quarter so the user sees what their career added during the period.

## Trigger phrases

- `quarterly review`
- `career review`
- `run quarterly career review`

## Modes

The script has three modes:

- `--mode prompt` (default): generate a Markdown prompt file with 10 quarterly review questions.
- `--mode snapshot`: copy current `experience.json` to `master/snapshots/experience_<date>.json`. Run at the end of each review session.
- `--mode diff`: compare current `experience.json` against the most recent snapshot, output a diff of new roles, new bullets per existing role, new skills, new certifications, new public artifacts, and leadership signal changes.

## Procedure

### Standard quarterly run

1. User triggers `quarterly review`.
2. Claude runs `python3 scripts/quarterly_career_review.py --mode prompt` to generate the questions.
3. Claude walks through the prompts conversationally, capturing answers into `master/experience.json`.
4. After capture, Claude runs `--mode snapshot` to lock in this quarter's state.
5. Claude runs `--mode diff` (comparing against the previous quarter's snapshot) and reports the quarter's deltas to the user.

### Quarterly prompts

The script generates 10 prompts covering:

1. Most proud project this quarter (STAR format)
2. New quantified outcomes for existing roles
3. Mentees promoted or grew this quarter
4. New skills and frameworks
5. New certifications
6. Public artifacts (talks, articles, podcasts, OSS)
7. Leadership scope changes
8. Career motivation / targeting profile shifts
9. New salary band data
10. Updated one-line career narrative

## CLI usage

```bash
# Generate the review prompt
python3 scripts/quarterly_career_review.py --mode prompt

# After capture, snapshot
python3 scripts/quarterly_career_review.py --mode snapshot

# Three months later, diff
python3 scripts/quarterly_career_review.py --mode diff
```

## Scheduling via Cowork scheduled tasks

```
Create scheduled task:
  Cron: 0 9 1 1,4,7,10 *
  Prompt: "Run the quarterly career review using `python3 scripts/quarterly_career_review.py --mode prompt`. Walk me through the prompts and capture my answers into experience.json. End by snapshotting and diffing against the prior quarter."
```

## Output files

- `quarterly_review_prompt_<YYYY-MM-DD>.md` (the prompt file Claude walks through)
- `master/snapshots/experience_<YYYY-MM-DD>.json` (locked snapshot per quarter)
- `quarterly_career_diff_<YYYY-MM-DD>.md` (delta report)
