# careerflow Discovery Scan Index

The complete catalog of optional discovery scans. All scans are optional. All read the user targeting profile from `master/experience.json -> targeting` and dedupe against `applications.xlsx`. Output goes to `candidates_v<N>_<scan_name>.md` (or a scan-specific output) in the workspace root.

## Quick reference

| Scan | Trigger phrase | What it surfaces | Cadence |
|------|----------------|------------------|---------|
| S&P 500 short list | `run S&P 500 scan` | Roles at S&P 500 companies in user's industries | Weekly |
| Series B/C funding | `run funding round scan` | Roles at growth-stage startups | Bi-weekly |
| Layoff comeback | `run layoff scan` | Roles at companies rebounding from layoffs | Monthly |
| IPO / S-1 | `run IPO scan` | Roles at post-IPO and S-1 filing companies | Monthly |
| Aggregator sweep | `run aggregator sweep` | Roles from Indeed, Built In, Wellfound, etc. | Weekly |
| LinkedIn sync | `sync LinkedIn searches` | Roles from user's LinkedIn saved searches | Weekly |
| Stealth / pre-launch | `run stealth scan` | Stealth startups with notable founders | Monthly |
| Recruiter / search firm | `run recruiter scan` | Executive recruiters to engage | Quarterly |
| Earnings hiring signal | `run earnings scan` | Companies with positive hiring quotes in earnings calls | Quarterly |
| Conference / event | `run event scan` | Sponsors/exhibitors at upcoming industry events | Quarterly |
| M&A acquisition | `run M&A scan` | Acquirer companies in last 12 months | Monthly |
| PE-backed portfolio | `run PE portfolio scan` | Companies in major PE firm portfolios | Quarterly |
| Geographic metro | `run [metro] scan` | All scans filtered to one geographic metro | As-needed |
| Culture fit | `run culture scan on candidates_v<N>` | Re-rank existing candidate list by Glassdoor data | Per batch |
| Salary band check | `check salary band for [role] at [company]` | Defensible salary range from multiple sources | Per application + offer |
| Followup nudge | `run followup scan` | Applications needing followup | Weekly |
| Alumni network | `scan alumni network` | Warm intros from school + prior employer overlaps | Weekly |

## When to use which

- **Active job hunt, broad surface**: S&P 500, funding round, aggregator sweep, LinkedIn sync.
- **Geographic constraint**: Metro deep dive.
- **Stretch ambition**: Stealth, recruiter scan.
- **Quality re-ranking**: Culture fit scan on top of any other.
- **Active pipeline care**: Followup nudge, alumni network.
- **Negotiation prep**: Salary band check.
- **Macro signal pickup**: Earnings, M&A, PE portfolio, IPO.
- **Networking play**: Conference / event, recruiter scan, alumni network.

## How a scan run works

1. User says trigger phrase.
2. Claude reads the corresponding `docs/<scan>_runtime.md` for procedure.
3. Claude reads `master/experience.json` for user targeting profile and `applications.xlsx` for dedupe.
4. Claude fans out WebSearch calls per the runtime procedure.
5. Claude scores results against targeting profile (include / drop / tier).
6. Claude writes the output file in the workspace root.
7. Claude reports a summary in chat with the recommended apply order or next steps.

## All scans are optional

The user is never required to run any scan. Discovery is opt-in by trigger phrase. The application skill handles individual job URLs the user pastes regardless of scan history.

## Scan combinations

Some scans layer on others:
- **Culture scan** takes any existing `candidates_v<N>.md` as input.
- **Metro deep dive** runs all base scans then filters to one metro.
- **Followup scan** reads only `applications.xlsx`, not any candidate list.
- **Salary band check** can be run standalone, or invoked by Claude during an application.

## Customization

Each runtime doc is editable. Users can:
- Add or remove search seed terms
- Change cadence recommendations
- Add new ATS or aggregator domains
- Tune filter strictness

The trigger phrase reads the doc at runtime, so changes take effect immediately on the next scan.
