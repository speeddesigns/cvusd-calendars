# CVUSD Calendar Atlas project instructions

Before changing calendar collection, the public dataset, or the web viewer,
read these files in order:

1. `.specify/memory/constitution.md`
2. `.specify/feature.json` and the active feature specification it names
3. `docs/platform-direction.md`
4. `KNOWLEDGE.md`
5. `README.md`

This repository is an independent Dooley World application published at
`cvusd.dooley.world`. The local constitution contains the complete adopted
Dooley World baseline plus CVUSD-specific rules. Local rules may be stricter but
must not weaken the baseline.

- Treat `scripts/build_dataset.py` as the source of truth for discovery,
  normalization, supplements, and de-duplication.
- Keep the dated archive in `data/` and the UI mirror at
  `public/data/cvusd_events.json` in sync. The builder does this by default.
- Preserve the collection window semantics: `--end` is inclusive, while all-day
  event `end` fields are exclusive.
- Query ParentSquare SmartSites APIs in month-sized intervals. Larger ranges
  have returned HTTP 500 responses.
- Do not combine a Google ICS feed with the matching SmartSites feed when the
  Google calendar is marked `covered_by_organization_smartsites_api`; that
  reintroduces recurrence duplicates.
- Keep provenance on every event (`source_calendar` and `published_via`) and
  retain unavailable-source notes rather than silently dropping them.
- Keep the public viewer static and read-only. A database, backend, account
  system, or cross-project data access requires a new specification and
  constitution review.
- If a source, workaround, or coverage gap changes, update `KNOWLEDGE.md` in the
  same change.
- Run the dataset validation checks in `KNOWLEDGE.md`, then run `npm test` after
  application or deployment changes.
- Use Spec Kit in order for material work: specify, clarify if needed, plan,
  tasks, analyze, then implement.
- Never commit service-account keys, source credentials, tokens, or secrets.
