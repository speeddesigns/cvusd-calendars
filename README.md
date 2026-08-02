# CVUSD Calendar Atlas

CVUSD Calendar Atlas is a community-built, source-linked view of public events
published by Castro Valley Unified School District and its school and program
websites. It is the first independent Dooley World project and is intended for
`https://cvusd.dooley.world`.

This is not an official district service. Dates can change; follow an event's
source link to confirm time-sensitive details.

## What is included

- A normalized public JSON dataset covering August 2, 2026 through August 2,
  2027, inclusive.
- 1,052 event occurrences from 26 publication calendars and 16 underlying
  source calendars across the district and 17 school/program sites.
- A static, responsive React explorer with text, month, organization,
  school-level, weekday, event-type, start-time, and source-format filters.
- Source provenance, coverage notes, crawl diagnostics, and a reproducible
  collection script.

## Repository layout

- `src/` - static calendar explorer source.
- `public/data/cvusd_events.json` - deployable dataset mirror.
- `data/cvusd_events_2026-08-02_to_2027-08-02.json` - dated canonical archive.
- `scripts/build_dataset.py` - source discovery, collection, normalization,
  supplements, recurrence expansion, and de-duplication.
- `KNOWLEDGE.md` - source map, API behavior, gaps, and refresh runbook.
- `.specify/` and `specs/` - adopted Dooley World constitution and feature specs.
- `AGENTS.md` - durable instructions for Codex and other automated contributors.

## Local development

Requirements: Node.js 24 and npm 10 or newer.

```powershell
npm install
npm run dev
```

Run the production checks with:

```powershell
npm test
```

The viewer is static. It loads the generated JSON once and performs all search
and filtering in the browser; it has no database, application API, account
system, or background service.

## Refreshing the dataset

Run with Python and `python-dateutil`:

```powershell
python scripts/build_dataset.py `
  --start 2026-08-02 `
  --end 2027-08-02 `
  --output data/cvusd_events_2026-08-02_to_2027-08-02.json
```

The `--end` argument is inclusive. All-day event `end` fields in the output are
exclusive. By default, a successful refresh also updates
`public/data/cvusd_events.json`; use `--skip-web-output` only for scratch runs.

Read `KNOWLEDGE.md` before changing collection logic or refreshing the window.
It records source-specific decisions that are easy to lose, including monthly
SmartSites query intervals and cross-publication recurrence de-duplication.

## Hosting and deployment

The production build is a static Vite bundle in `dist/` and is configured for a
dedicated Firebase Hosting project. The CVUSD project owns its deployment,
security, budget, quota, and failure boundary separately from the
`dooley.world` hub.

Production deployment uses GitHub Actions and Google Workload Identity
Federation. No service-account key or other long-lived Google credential belongs
in GitHub or this repository.

## Governance

The local constitution adopts Dooley World Constitution 1.0.0 in full and adds
CVUSD-specific rules for reproducible source-linked data and honest coverage.
Project specifications may add stricter constraints but cannot weaken that
baseline.
