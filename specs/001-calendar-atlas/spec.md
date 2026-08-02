# Feature Specification: CVUSD Calendar Atlas

**Feature Branch**: Not created (no `before_specify` branch hook is configured)

**Created**: 2026-08-02

**Status**: Baseline

**Input**: Establish the existing CVUSD Calendar Atlas as the first independent
Dooley World project: a public, source-linked calendar explorer at
`cvusd.dooley.world` backed by a reproducible normalized dataset.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find Relevant School Events (Priority: P1)

As a community member, I can search and filter public district and campus
events so that I can quickly find dates relevant to my family or organization.

**Why this priority**: Discovering relevant events is the project's primary value.

**Independent Test**: Load a validated dataset, apply combinations of text,
month, organization, school-level, weekday, timing, start-time, and source
filters, and verify that every visible result satisfies the selected criteria.

**Acceptance Scenarios**:

1. **Given** the public dataset is available, **When** a visitor opens the
   explorer, **Then** events are shown chronologically with their date, title,
   time state, publishing organization, and source type.
2. **Given** a visitor applies one or more filters, **When** results update,
   **Then** every result matches all active filter groups and the result count is
   understandable.
3. **Given** no event matches, **When** filters are active, **Then** the visitor
   sees an intentional empty state and can clear the filters.

---

### User Story 2 - Verify an Event at Its Source (Priority: P1)

As a visitor, I can inspect an event's provenance and open an official source so
that I can confirm time-sensitive details.

**Why this priority**: Aggregated calendar information can change; provenance
is essential to trustworthy use.

**Independent Test**: Open event details for records from each supported source
type and verify that source identity, publishing organizations, uncertainty,
and an available official destination are presented accurately.

**Acceptance Scenarios**:

1. **Given** a visitor opens an event, **When** details appear, **Then** the date,
   time state, location when known, description when known, source calendar, and
   publishing organizations are readable.
2. **Given** an official destination is available, **When** the visitor follows
   it, **Then** ordinary browser navigation opens the source with a meaningful label.
3. **Given** an end time is not published, **When** the event is shown, **Then**
   the project explicitly says the end time is unknown rather than inventing one.

---

### User Story 3 - Understand Coverage and Freshness (Priority: P2)

As a visitor, I can understand the dataset window, rebuild date, coverage, and
known source errors so that I do not mistake the atlas for an authoritative
real-time district system.

**Why this priority**: The application aggregates public sources and must be
honest about the limits of that process.

**Independent Test**: Provide datasets with complete coverage, documented
unavailable sources, and understood source errors; verify that the interface and
supporting documentation do not overstate completeness.

**Acceptance Scenarios**:

1. **Given** a validated dataset, **When** the page loads, **Then** the visitor
   can identify its date window, last rebuild date, event count, organization
   coverage, and source-error count.
2. **Given** an organization has no discovered public calendar, **When** the
   dataset is inspected, **Then** that condition remains recorded as an observed
   coverage gap rather than evidence that the organization has no events.
3. **Given** the dataset cannot be loaded, **When** the request fails, **Then**
   the visitor sees a clear unavailable state rather than an empty calendar.

---

### User Story 4 - Refresh Reproducibly (Priority: P2)

As the project owner, I can rebuild the dataset from documented sources and
validate it before release so updates do not silently change identity, coverage,
provenance, or temporal semantics.

**Why this priority**: The public viewer is only as reliable as its collection
and validation process.

**Independent Test**: Rebuild a fixed date window twice from unchanged source
inputs and verify deterministic identities, ordering, metadata, provenance, and
matching archive/UI outputs.

**Acceptance Scenarios**:

1. **Given** the documented sources are reachable, **When** a refresh succeeds,
   **Then** it produces a dated archive and a byte-identical deployable mirror.
2. **Given** the same source event appears through multiple publication paths,
   **When** records are reconciled, **Then** one occurrence retains all known
   publication paths without recurrence duplicates.
3. **Given** a source is unavailable or changes behavior, **When** collection
   completes, **Then** the condition is retained in diagnostics and documentation
   before release approval.

### Edge Cases

- All-day event end dates are exclusive even though the requested collection
  window end is inclusive.
- Timed events retain explicit UTC offsets and display in the dataset timezone.
- Unknown end times remain unknown and do not acquire an inferred duration.
- Same-title events at the same time remain distinct when their source identities differ.
- Events exposed through both a district aggregate and a campus calendar are not
  automatically classified as districtwide.
- Long content wraps without hiding actions or requiring horizontal scrolling.
- Filter combinations with zero matches do not look like a load failure.
- A missing, malformed, or unavailable dataset produces an error state.
- The details panel closes with Escape, contains keyboard focus while open, and
  returns focus to the event that opened it.
- Motion is not required to understand or operate the page and respects reduced motion.

## Requirements *(mandatory)*

### Scope Boundaries

This feature includes public-source discovery, normalized occurrence data,
documented supplements, provenance and coverage diagnostics, local filtering,
event details, responsive delivery, and a public Dooley World project entry. It
excludes accounts, private calendars, visitor submissions, background refreshes,
notifications, a database, an application backend, and claims of official CVUSD
ownership or endorsement.

### Functional Requirements

- **FR-001**: The project MUST publish one normalized occurrence dataset for a
  declared inclusive date window and timezone.
- **FR-002**: Every event MUST have a deterministic unique identity, title,
  start, end, all-day state, timezone, source calendar, and one or more known
  publication paths.
- **FR-003**: Unknown descriptions, locations, URLs, or end times MUST remain
  distinguishable from known values.
- **FR-004**: The dataset MUST inventory publication calendars, underlying
  source calendars, reference sources, discovered organizations, unavailable
  calendars, and collection errors.
- **FR-005**: Exact duplicates MUST be removed without merging distinct source
  identities merely because their visible details match.
- **FR-006**: Matching SmartSites and Google publication paths MUST NOT be
  ingested twice when one is documented as covered by the other.
- **FR-007**: A successful refresh MUST produce a dated archive and a
  byte-identical deployable mirror.
- **FR-008**: The public viewer MUST load the generated dataset without requiring
  an account, database, or application API.
- **FR-009**: Visitors MUST be able to filter by text, month, organization,
  school level, weekday, all-day/timed state, timed-event start range, and source type.
- **FR-010**: Active filters MUST combine predictably, expose their current
  state, and be resettable.
- **FR-011**: Results MUST appear in chronological groups and disclose how many
  events match.
- **FR-012**: Event details MUST show available descriptive information,
  provenance, uncertainty, and an official source destination when available.
- **FR-013**: The page MUST distinguish loading, load failure, and zero-result states.
- **FR-014**: The page MUST disclose the dataset rebuild date, collection window,
  event count, publication-calendar count, organization count, and source-error count.
- **FR-015**: All filters, event cards, details, and source links MUST be usable
  by keyboard and exposed with meaningful names, roles, focus order, and state.
- **FR-016**: Text and meaningful visual elements MUST meet WCAG 2.2 AA contrast,
  and information MUST NOT rely on color alone.
- **FR-017**: The experience MUST remain readable and operable from 320 CSS
  pixels through large desktop widths and at 200% browser zoom without loss of
  information or two-dimensional page scrolling.
- **FR-018**: The canonical public address MUST be `cvusd.dooley.world`, and the
  Dooley World hub MUST link to it as an independently deployed project.
- **FR-019**: The project MUST identify itself as a community index assembled
  from official public sources and MUST NOT imply CVUSD ownership or endorsement.

### Key Entities

- **Calendar Event**: One normalized occurrence with temporal details, content,
  source identity, provenance, and uncertainty fields.
- **Publication Calendar**: A public surface through which events were observed,
  including its organization, endpoint, ingestion state, and coverage notes.
- **Source Calendar**: The underlying event feed represented by normalized records.
- **Dataset Snapshot**: A versioned collection window with events, inventories,
  reference coverage, diagnostics, counts, timezone, and generation metadata.
- **Organization Coverage**: The observed state of an official district, school,
  or program website and whether a distinct public event calendar was discovered.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 4 of 5 first-time visitors can find a requested event or
  conclude that no matching event is present within 30 seconds.
- **SC-002**: 100% of displayed events map to exactly one normalized event ID and
  show at least one source or publication path.
- **SC-003**: In validation, unique event ID count, metadata event count, and
  actual event count are identical, and the archive and deployable mirror are
  byte-for-byte equal.
- **SC-004**: 100% of events fall inside the declared inclusive collection
  window and remain sorted by start, normalized title, and identity.
- **SC-005**: Every unavailable source or collection error is either resolved or
  explicitly documented before release.
- **SC-006**: Keyboard-only users can operate every filter, open and close event
  details, follow an official source, and recover focus without an unlabeled control.
- **SC-007**: At widths from 320 through 1920 CSS pixels and at 200% zoom, all
  content remains available without horizontal page scrolling.
- **SC-008**: All tested text and meaningful visual elements meet WCAG 2.2 AA
  contrast thresholds.
- **SC-009**: On a typical current mobile device using standard broadband, the
  page shell and dataset status become understandable within 2 seconds for at
  least 95% of measured visits.
- **SC-010**: The canonical address serves valid HTTPS and remains isolated from
  a failure or deployment of the Dooley World hub.

## Assumptions

- The project covers public English-language information and does not collect
  visitor data.
- Source organizations remain authoritative; visitors should confirm
  time-sensitive details at the linked source.
- The owner performs refreshes deliberately rather than on a background schedule.
- Static client-side filtering is sufficient for the current dataset size.
- Final project copy and release status are approved by the repository owner.
