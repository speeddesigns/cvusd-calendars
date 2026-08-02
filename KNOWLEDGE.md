# CVUSD calendar collection knowledge

This file is the handoff for the next refresh. It records the source map, non-obvious behavior, and decisions that are expensive to rediscover.

## Current snapshot

- Collection window: 2026-08-02 through 2027-08-02, inclusive.
- Canonical archive: `data/cvusd_events_2026-08-02_to_2027-08-02.json`.
- UI mirror: `public/data/cvusd_events.json`.
- Result: 1,052 normalized occurrences, 26 publication calendars, 16 underlying source calendars, and zero source errors.
- Coverage: the district plus 17 official school/program sites (18 organizations total).
- Exact source records removed during reconciliation: 796.

The JSON is also a machine-readable research log. `publication_calendars` contains every discovered calendar surface and endpoint, `source_calendars` describes the feeds represented in the event list, and `discovery` records official organizations, calendar pages, unavailable calendars, external links, and errors.

## Source map

### ParentSquare SmartSites

Most official sites use ParentSquare SmartSites. Calendar configuration is embedded in page HTML as an `application/json` script with the data view `data-view-data-events-sliders`. The useful field is `calendarApiID`.

The event endpoint is:

```text
https://{site}/api/calendars/{calendarApiID}/events?start_date={YYYY-MM-DD}&end_date={YYYY-MM-DD}&view_source=full-calendar
```

Known API calendar IDs in this snapshot:

| Organization | ID |
| --- | ---: |
| District aggregate | 137799 |
| Adult and Career Education | 138555 |
| Castro Valley Elementary | 137802 |
| Chabot Elementary | 137803 |
| Independent Elementary | 137808 |
| Jensen Ranch Elementary | 137810 |
| Marshall Elementary | 137804 |
| Palomares Elementary | 137805 |
| Proctor Elementary | 137806 |
| Stanton Elementary | 137809 |
| Vannoy Elementary | 137807 |
| Canyon Middle | 137812 |
| Creekside Middle | 137813 |
| Castro Valley High | 137811 |

Request one month at a time. Broad date ranges can produce HTTP 500 even when the calendar and dates are valid. `iter_month_intervals()` implements this workaround.

SmartSites responses may contain events from multiple underlying feeds. The stable identity is built from source event data, not from the publication calendar that exposed it. `published_via` is then unioned so one occurrence can show both its district and campus publication paths.

### Public Google calendars

Official pages expose several public Google Calendar IDs. Their exact IDs and ICS URLs are stored in `publication_calendars`; do not maintain a second manual list here. The discovery code extracts Google iframe IDs and constructs the public `basic.ics` URL.

Important de-duplication rule: when a Google calendar is also surfaced through the organization’s SmartSites API, its publication record is marked `covered_by_organization_smartsites_api` and the ICS event body is not unioned into the dataset. SmartSites sometimes rewrites Google IDs or recurrence suffixes, so ingesting both paths creates false duplicates.

### Instructional calendar PDF

- Landing page: https://www.cv.k12.ca.us/district-instructional-calendar
- Approved 2026-2027 PDF: https://files.smartsites.parentsquare.com/8941/cvusd_calendar_-_2026-27_approved_20251022.pdf

The PDF is a visual calendar, not a reliable structured feed. Its 50 important dates were visually verified and transcribed into `INSTRUCTIONAL_CALENDAR_EVENTS`. They include the first/last day, no-school days, breaks, grade-band minimum days, work/staff-development days, quarters/semesters, and elementary reporting milestones.

When a new PDF replaces it, render every page and verify the legend as well as the date cells. Update the URL, the static supplement, and its reference note together. All-day output uses an exclusive `end` date.

### CVHS athletics

- Replacement page: https://sites.google.com/cv.k12.ca.us/cvhsathletics/calendar
- Legacy conference link: https://westalamedacountyconference.org/public/genie/678/school/5/

At collection time the replacement page published seven 6:00 p.m. Athletic Boosters parent meetings but said 2026-2027 home-game dates were coming soon. The legacy link redirected to a generic Arbiter migration page, so no game feed was available. The seven meetings are in `ATHLETICS_BOOSTER_EVENTS`; because no end time was published, `end_time_known` is `false`.

Recheck both pages on every refresh. Replace the static meetings with a structured public feed if one appears.

### Organizations without distinct event calendars

At collection time these official sites did not expose a distinct public event calendar:

- Alma State Preschool
- Redwood High School
- Castro Valley Virtual Academy 9-12
- Roy Johnson Adult Transition

This is an observed availability condition, not a claim that the organizations have no events. Keep it in `discovery.organizations_without_discovered_event_calendar` and recheck on the next run.

Classified employee work-year calendars are intentionally outside the public-event scope.

## Normalization and identity

- The dataset timezone is `America/Los_Angeles`.
- Timed values include an explicit UTC offset.
- All-day values are dates and use an exclusive `end`.
- Output is occurrence-level, so recurring events are expanded inside the requested window.
- Event IDs are deterministic hashes of normalized source identity and occurrence details.
- Events sort by start, then title, then ID.
- Only exact source duplicates are removed. Two same-title events at the same time remain separate when their source identities differ; that avoids silently merging legitimate campus events.
- HTML descriptions are retained as `description`, with a plain-text `description_text` for search and display.
- Every event retains `source_calendar` and one or more `published_via` records.

## Refresh recipe

From the repository root:

```powershell
python scripts/build_dataset.py `
  --start 2026-08-02 `
  --end 2027-08-02 `
  --output data/cvusd_events_2026-08-02_to_2027-08-02.json
```

The builder automatically writes the UI mirror to `public/data/cvusd_events.json`. Use `--skip-web-output` only when intentionally producing a scratch dataset, or provide a different mirror path with `--web-output`.

For a later rolling window, change the dates and dated archive filename. Then update this file’s snapshot section and the README. Review any changed source errors, organization coverage, and availability notes instead of comparing only the event count.

## Validation checklist

Run this after collection:

```powershell
$dataset = Get-Content data/cvusd_events_2026-08-02_to_2027-08-02.json -Raw | ConvertFrom-Json
$dataset.metadata | ConvertTo-Json
($dataset.events.id | Sort-Object -Unique).Count
$dataset.events.Count
$dataset.discovery.errors.Count
```

Confirm that:

1. The unique ID count equals `events.Count`.
2. `metadata.event_count` equals `events.Count`.
3. Events fall inside the inclusive collection window.
4. Events are sorted by start, case-folded title, and ID.
5. `discovery.errors` is empty or every error is understood and documented.
6. The dated archive and UI mirror are byte-for-byte identical.
7. `npm test` succeeds from the repository root.

Useful discovery-only check:

```powershell
python scripts/build_dataset.py --discover-only
```

## Web viewer

The app at the repository root is deliberately static: it fetches the mirrored JSON file and filters locally. There is no database, account, or background service to reconstruct. Its source links are taken directly from each event’s provenance.

School level is a UI-derived field based on non-district organizations in `published_via`. Elementary campuses map to Elementary; Canyon and Creekside map to Middle school; CVHS, Redwood, and Virtual Academy map to High school; CVACE and Roy Johnson map to Adult & transition; Alma maps to Early learning. If no mapped non-district organization is present, the event is Districtwide. Do not classify an event as Districtwide merely because it also appears through the district aggregate calendar.

Local development:

```powershell
cd web
npm run dev
```

Production verification:

```powershell
npm run build
```

The key maintenance invariant is simple: refresh with the builder, let it update both JSON files, then rebuild the site.
