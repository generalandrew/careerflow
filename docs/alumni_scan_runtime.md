# Alumni Network Scan Runtime

Optional runtime that reads the user's school and prior employer history from `master/experience.json` and surfaces companies in the user's pipeline where alumni currently work. Output is a list of warm intro candidates per application.

## Trigger phrases

- `scan alumni network`
- `find warm intros for my pipeline`
- `alumni at [Company]`

## Inputs

- `master/experience.json -> education` (school names)
- `master/experience.json -> roles[]` (prior employer names)
- `applications.xlsx` companies (the user's pipeline)
- User's LinkedIn profile URL (for alumni filter)

## Procedure

1. Build the user's alumni signal set: list of schools + list of prior employers.
2. For each company in `applications.xlsx` (with status not yet `Rejected` or `Closed`):
   - Search LinkedIn for "[School] alumni at [Company]" and "[Prior Employer] alumni at [Company]"
   - Capture top 3 alumni per company with: name, current role, mutual connection if known, LinkedIn URL
3. Compile into `warm_intros_<YYYY-MM-DD>.md` grouped by company.
4. For each entry, generate a draft LinkedIn message asking for a 20-minute intro coffee or virtual chat.

## Output schema

Per company:
- Company name, role applied for, status, days since applied
- Alumni list (max 3 per company):
  - Name, title, LinkedIn URL, mutual connection (if any), school/employer overlap
  - Draft intro message tailored to the overlap

## Notes

- LinkedIn alumni search is rate-limited. Recommend the user do the LinkedIn searches manually and paste results back.
- Strongest signal is shared employer (former co-worker) over shared school.
- Recommended cadence: weekly, after new applications are submitted.
