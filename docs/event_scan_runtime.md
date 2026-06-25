# Conference / Industry Event Scan Runtime

Optional discovery runtime that identifies upcoming industry conferences in the user's target domains and maps to companies sponsoring or exhibiting plus their open roles. Conference networking + targeted application combo.

## Trigger phrases

- `run event scan`
- `scan upcoming conferences`
- `find conferences for my targeting`

## Inputs

- Date window, default next 6 months.
- User targeting profile from `master/experience.json -> targeting`.
- Geographic preferences from `preferences.geographic_constraints` for in-person attendance feasibility.

## Procedure

1. Build event search queries from `target_job_types` + `industry_preferences`. Example: "Solutions Engineer conference 2026", "AI infrastructure summit 2026", "fintech conference Q3 2026".
2. Fan out WebSearch calls for major industry events:
   - Software/SaaS: Dreamforce, AWS re:Invent, Google Cloud Next, KubeCon, SaaStr Annual
   - AI/ML: NeurIPS, ICML, AI Engineer Summit, Anthropic Dev Day
   - Fintech: Money 20/20, Fintech Meetup, Finovate
   - Cybersecurity: RSA Conference, Black Hat, DEF CON
   - DevOps: KubeCon, DockerCon
   - Sales/GTM: SaaStr, Pavilion CRO Summit, RevOps Co-op
3. For each event in the date window, capture: name, date, location, in-person/virtual/hybrid, sponsor list, exhibitor list.
4. For each sponsor/exhibitor company, run a careers page scan for openings matching the targeting profile.
5. Compile into `candidates_v<N>_events.md` with two views:
   - Per company, openings + event context
   - Per event, list of in-scope companies attending

## Notes

- For high-fit events, recommend the user actually attend (in person or virtual) for warm intro opportunities.
- Sponsor companies usually have larger booths and more aggressive hiring.
- Recommended cadence: quarterly, aligned to conference calendar.
