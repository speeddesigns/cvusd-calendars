# CVUSD Calendar Atlas web app

Static, responsive explorer for the normalized Castro Valley Unified School District event dataset.

## Data flow

The collection script in the parent repository writes `public/data/cvusd_events.json`. The browser loads that file once and performs search, month, organization, school-level, weekday, event-type, start-time, and source-format filtering locally. No database or runtime API is required.

School level is derived from the event's non-district publishing organization. This prevents the district's aggregate calendar from making every campus event appear districtwide. Events without a mapped campus organization are classified as districtwide.

Custom time ranges apply to timed events using their published start time. The range uses 30-minute increments; all-day events remain available through the event-type filter.

## Development

```powershell
npm install
npm run dev
```

Validation:

```powershell
npm run lint
npm test
```

The production deployment is configured in `.openai/hosting.json`.
