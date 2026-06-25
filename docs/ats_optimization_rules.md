# ATS Optimization Rules and Per-ATS Playbook

The authoritative reference for Applicant Tracking System (ATS) parsing optimization in careerflow. Three sections: content rules, format rules, per-ATS playbook.

## Why this matters

Most employer applications route through ATS parsing before a human reads the resume. The parser extracts name, contact, work history, dates, education, and skills into a structured database. If the parser misreads or skips a field, the candidate is filtered or downranked before any human review. ATS optimization is the highest-leverage change to apply velocity.

---

## Content Rules

### Section headings

Use unambiguous standard section names. Variations like "Professional History" or "My Career" confuse ATS regex patterns. Use:

- Summary
- Core Competencies
- Professional Experience
- Technical Skills
- Education
- Certifications
- Projects (optional)

### Date format

ATS parsers expect canonical formats:

- `Mar 2021 - Apr 2023` (preferred)
- `03/2021 - 04/2023`
- `2021 - 2023` (year only, less precise)

Always include a real `Present` or `Current` for active roles.

### Job title and company line

Single line, easily parseable: `Senior Solution Principal, Acme    March 2018 - April 2023`. Title first, then company, then dates right-aligned via tab.

### Bullets

Use standard bullet character (`•`). Each bullet one to two lines. Start with a strong verb. Quantify when possible.

### Keywords / JD vocabulary

Mirror exact phrases from the JD in the Summary and Skills sections. Include both acronyms and full terms (`API` and `Application Programming Interface`) at least once. Weave JD vocabulary into Experience bullets too, not just top sections.

### Sanitizer rules (v1.1)

The renderer (`scripts/build_resume.js`) applies these rules:

- Date ranges with dashes preserved (`Mar 2021 - Apr 2023`)
- `Email:`, `Phone:`, `LinkedIn:` labels preserved
- All other dashes normalized to natural language ("20 to 30%", "$4M to $8M")
- Compound modifiers split ("multi year" not "multi-year")
- Colons stripped except in whitelisted labels
- Semicolons replaced with commas
- Em dashes removed, en dashes converted to "to"

### Personal information

- Name on its own line, prominent.
- Contact line includes location, labelled phone, labelled email, LinkedIn URL.
- Avoid date of birth, gender, marital status, photo.

### File name

`<CandidateName>_Resume_<Company>.docx`. No spaces, underscore or hyphen separators, total length under 50 chars.

---

## Format Rules

### File format

DOCX is the only output format. Every major ATS parses DOCX cleanly. PDF parsing quality varies and is not produced by default. If an employer explicitly requires PDF, generate manually outside the pipeline.

### Layout

Single column only. Multi-column layouts break ATS parsing because the parser reads top-to-bottom of column 1 then column 2, jumbling content.

The standard render uses a single tab-stop "visual" 2-column for Core Competencies. The conservative render collapses this to single-column bullets.

### Tables, headers, footers, text boxes, graphics

None. All of these are invisible to ATS parsers or wreck parsing order.

### Fonts

Calibri (default), Arial, Times New Roman, Helvetica, Cambria, Georgia. Avoid decorative or custom fonts.

### Font sizes

- Body 10-12 pt
- Section headers 12-14 pt
- Name 18-24 pt

### Page size and margins

US Letter (8.5 x 11 inches). Margins 0.5 to 1.0 inch.

### Length

Two pages standard for senior roles. ATS handles multi-page DOCX fine.

---

## Conservative Render Variant

Triggered by `--conservative` flag, set automatically by `apply.py` when `ats_detector.py` returns `use_conservative_render = true`. Fail-unsafe logic, applied when:

- ATS is identified as legacy (Taleo, classic iCIMS, JazzHR)
- ATS cannot be identified (unknown URL pattern)

Conservative variant:
- Disables decorative bottom borders on section headers
- Collapses Core Competencies to single column bullets
- Uses black text throughout (no accent color)

---

## Per-ATS Playbook

| ATS | URL pattern examples | Parser quality | is_legacy | Known quirks |
|-----|---------------------|----------------|-----------|--------------|
| Greenhouse | `job-boards.greenhouse.io/<co>/jobs/<id>` | Excellent | false | Modern, robust keyword extraction |
| Ashby | `jobs.ashbyhq.com/<co>/<uuid>` | Excellent | false | Most modern parser |
| Lever | `jobs.lever.co/<co>/<uuid>` | Excellent | false | Robust |
| Workday | `<co>.wd*.myworkdayjobs.com` | Very good | false | Auto-fills app form from resume |
| SmartRecruiters | `jobs.smartrecruiters.com/<co>` | Very good | false | Modern |
| iCIMS | `<co>.icims.com` | Mixed | true | Older versions strict, treat as legacy fail-unsafe |
| Taleo | `<co>.taleo.net` | Poor | true | Very old parser |
| Oracle Fusion HCM | `*.fa.us2.oraclecloud.com` | Good | false | Modern Oracle product |
| Amazon ATS | `amazon.jobs` | Good | false | Internal proprietary |
| Microsoft careers | `jobs.careers.microsoft.com` | Good | false | Workday based |
| LinkedIn Easy Apply | `linkedin.com/jobs/view/<id>` | Excellent | false | LinkedIn pulls profile data directly |
| Jobvite | `jobs.jobvite.com/<co>` | Good | false | Solid modern parser |
| Rippling | `ats.rippling.com/<co>/jobs/<uuid>` | Good | false | Modern |
| BambooHR | `<co>.bamboohr.com/jobs/` | Good | false | Smaller employers typically |
| Workable | `apply.workable.com/<co>` | Good | false | Modern |
| JazzHR | `<co>.applytojob.com` | Mixed | true | Older, treat as legacy fail-unsafe |
| Unknown | (no pattern match) | n/a | n/a | Conservative render applied per fail-unsafe rule |

To add a new ATS pattern, edit the `ATS_PATTERNS` list in `scripts/ats_detector.py`. Order matters only when patterns might overlap; place more specific patterns first.
