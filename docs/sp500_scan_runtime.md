# S&P 500 Short List Scan Runtime

Chat-driven discovery runtime to surface live Director / Senior Manager / Principal openings across the S&P 500 short list filtered to the user's industry and skill criteria.

## Trigger phrases

- `run S&P 500 scan`
- `run sp500 scan`
- `scan the short list`

## Inputs

- The 55-company short list maintained in this file (section "Short list, edit per user").
- Pipeline dedupe source: `applications.xlsx` Company column. Drop any company already in pipeline.
- **User targeting profile from `master/experience.json -> targeting`**:
  - `target_job_types` — only surface roles matching these families
  - `target_seniority_levels` — only surface roles at these tiers
  - `exclude_job_types` — drop matches in these families
  - `exclude_seniority_levels` — drop matches at these tiers
  - `industry_preferences` and `industry_exclusions` — already applied to the short list, but re-check per surfaced role

## Procedure

1. Load the short list from this file.
2. Load `applications.xlsx`, build a Set of unique Company values, remove from scan list.
3. Load the user targeting profile from `master/experience.json -> targeting`. Build the search query terms from `target_job_types` and `target_seniority_levels`. Example: if target_job_types = ["Solutions Engineer", "Forward Deployed Engineer"] and target_seniority_levels = ["Senior", "Principal", "Director"], the per-company query becomes "Acme Senior OR Principal OR Director Solutions Engineer OR Forward Deployed Engineer remote 2026".
4. Fan out parallel WebSearch calls in batches of 4, one search per company, allowed_domains limited to the company's careers domain (or top-level) when known.
5. For each result, score against the targeting profile:
   - **Include only if** the role title contains at least one of `target_job_types` AND at least one of `target_seniority_levels`.
   - **Drop if** the role title contains any of `exclude_job_types` OR any of `exclude_seniority_levels`.
   - Skip generic careers portal links with no specific role.
6. Compile results into `candidates_v<N>_sp500_picks.md` where N is the next integer after the highest existing `candidates_v*` file in the workspace root.
7. Group results into Tier 1 (direct fit, apply first), Tier 2 (strong fit), Tier 3 (watch list).
8. Report total live picks surfaced and recommended apply order in the chat reply. Include the targeting profile used at the top of the output for reproducibility.

## Output schema

The candidates_vN file has these sections:

- Title with date
- Source line (search seeds used, dedupe sources)
- Tier 1, Direct Fit, Apply First (5 max recommended)
- Tier 2, Strong Fit, Apply Second Wave (5 max recommended)
- Tier 3, Watch List (open ended)
- Companies scanned with no strong hit (list)
- Total live picks summary
- Recommended apply order
- Sources (markdown hyperlinks to each surfaced JD)

## Dedupe rule

Companies removed from scan if their name appears in any row of `applications.xlsx` Company column. Use case-insensitive exact match.

## Short list, edit per user

This is the seed list. Edit to match the user's industry, skill, and geographic preferences. The default below skews to software, SaaS, IT services, fintech, internet, consulting, tech-leaning consumer discretionary.

### Software and SaaS (27)

ADSK Autodesk, AKAM Akamai, ANSS Ansys, APP AppLovin, CDNS Cadence Design Systems, CRWD CrowdStrike, DDOG Datadog, EA Electronic Arts, FICO Fair Isaac, FTNT Fortinet, GEN Gen Digital, GDDY GoDaddy, INTU Intuit, JKHY Jack Henry, MANH Manhattan Associates, MSFT Microsoft, ORCL Oracle, PANW Palo Alto Networks, PAYC Paycom, PAYX Paychex, PLTR Palantir, PTC PTC Inc, ROP Roper Technologies, SNPS Synopsys, VRSN Verisign, VEEV Veeva Systems, ZS Zscaler.

### IT Services and Consulting (7)

ACN Accenture, CDW CDW, CTSH Cognizant, DXC DXC Technology, EPAM EPAM Systems, IBM IBM, CSCO Cisco (software arm).

### Fintech and Payments (6)

FI Fiserv, FIS Fidelity National Information Services, GPN Global Payments, MA Mastercard, PYPL PayPal, V Visa.

### Exchanges and Market Tech (3)

ICE Intercontinental Exchange, NDAQ Nasdaq, SPGI S&P Global.

### Data Services and Analytics (3)

EFX Equifax, IQV IQVIA, VRSK Verisk Analytics.

### HR and Payroll Tech (1)

ADP ADP.

### Internet, Digital Media, Digital Marketplaces (8)

ABNB Airbnb, BKNG Booking Holdings, EBAY eBay, ETSY Etsy, EXPE Expedia, META Meta Platforms, NFLX Netflix, UBER Uber.

## Filter logic (default, edit per user)

Keep: software, IT services, digital services, fintech, internet, consulting, tech-leaning consumer discretionary.

Drop: construction, hardware/device manufacturing, semiconductors, pure utilities, energy, materials, real estate, pure consumer staples, pure pharmaceuticals/medical devices, telecom carriers, banks/pure insurance, pure aerospace/defense, pure industrials.

## Refresh cadence

User can re-trigger this scan at any time. Recommended cadence: weekly. Each run produces a new `candidates_v<N>_sp500_picks.md` file. Older versions are kept as history.

## Customization

When the user identifies new in-scope or out-of-scope companies, edit the short list section above. When new companies enter the user's pipeline, no edit is needed here, the dedupe step reads `applications.xlsx` live each run.
