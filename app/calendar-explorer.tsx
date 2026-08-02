"use client";

import { useEffect, useMemo, useState } from "react";

type PublishedVia = {
  calendar_key: string;
  organization: string;
  calendar_page_url: string;
  endpoint: string;
};

type CalendarEvent = {
  id: string;
  source_event_id: string;
  title: string;
  start: string;
  end: string;
  end_time_known: boolean;
  all_day: boolean;
  timezone: string;
  description: string;
  description_text: string;
  location: string;
  url: string;
  source_calendar: {
    calendar_id: string;
    calendar_name: string;
    feed_id: string;
    feed_source: string;
  };
  published_via: PublishedVia[];
};

type Dataset = {
  metadata: {
    district: string;
    generated_at: string;
    timezone: string;
    window_start: string;
    window_end_inclusive: string;
    event_count: number;
    publication_calendar_count: number;
    source_calendar_count: number;
    official_organization_count: number;
    exact_duplicate_records_removed: number;
    source_error_count: number;
  };
  events: CalendarEvent[];
};

const DATASET_URL = "/data/cvusd_events.json";
const PAGE_SIZE = 60;

function Icon({ name }: { name: "arrow" | "calendar" | "clock" | "map" | "search" | "x" }) {
  const paths = {
    arrow: <><path d="M5 12h14"/><path d="m14 7 5 5-5 5"/></>,
    calendar: <><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/></>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    map: <><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></>,
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    x: <path d="m6 6 12 12M18 6 6 18"/>,
  };
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}

function localDate(value: string) {
  return new Date(`${value.slice(0, 10)}T12:00:00`);
}

function dateKey(event: CalendarEvent) {
  return event.start.slice(0, 10);
}

function monthKey(event: CalendarEvent) {
  return event.start.slice(0, 7);
}

function formatDay(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  }).format(localDate(value));
}

function formatMonth(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    year: "numeric",
  }).format(localDate(`${value}-15`));
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatEventTime(event: CalendarEvent) {
  if (event.all_day) return "All day";
  if (!event.end_time_known) return `${formatTime(event.start)} · end time not published`;
  return `${formatTime(event.start)}–${formatTime(event.end)}`;
}

function sourceLabel(source: string) {
  return ({
    google: "Google calendar",
    ss: "SmartSites",
    official_pdf: "Official PDF",
    official_webpage: "Official webpage",
  } as Record<string, string>)[source] ?? source;
}

function eventOrganizations(event: CalendarEvent) {
  return [...new Set(event.published_via.map((item) => item.organization))];
}

function EventDetails({ event, onClose }: { event: CalendarEvent; onClose: () => void }) {
  useEffect(() => {
    const closeOnEscape = (keyEvent: KeyboardEvent) => {
      if (keyEvent.key === "Escape") onClose();
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [onClose]);

  const organizations = eventOrganizations(event);
  const sourceUrl = event.url || event.published_via[0]?.calendar_page_url;

  return (
    <div className="detail-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="detail-panel" role="dialog" aria-modal="true" aria-labelledby="event-detail-title" onMouseDown={(mouseEvent) => mouseEvent.stopPropagation()}>
        <button className="icon-button" type="button" onClick={onClose} aria-label="Close event details"><Icon name="x" /></button>
        <p className="eyebrow">Event details</p>
        <h2 id="event-detail-title">{event.title}</h2>
        <div className="detail-facts">
          <p><Icon name="calendar" /><span>{formatDay(dateKey(event))}</span></p>
          <p><Icon name="clock" /><span>{formatEventTime(event)}</span></p>
          {event.location && <p><Icon name="map" /><span>{event.location}</span></p>}
        </div>
        {event.description_text && <p className="detail-description">{event.description_text}</p>}
        <div className="detail-section">
          <span className="detail-label">Published by</span>
          <div className="pill-row">
            {organizations.map((organization) => <span className="soft-pill" key={organization}>{organization}</span>)}
          </div>
        </div>
        <div className="detail-section">
          <span className="detail-label">Source</span>
          <p>{event.source_calendar.calendar_name} · {sourceLabel(event.source_calendar.feed_source)}</p>
        </div>
        {sourceUrl && (
          <a className="source-link" href={sourceUrl} target="_blank" rel="noreferrer">
            Open official source <Icon name="arrow" />
          </a>
        )}
        <p className="detail-note">Dates can change. Confirm time-sensitive details with the official source.</p>
      </section>
    </div>
  );
}

export function CalendarExplorer() {
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [loadError, setLoadError] = useState("");
  const [query, setQuery] = useState("");
  const [month, setMonth] = useState("all");
  const [organization, setOrganization] = useState("all");
  const [timing, setTiming] = useState("all");
  const [source, setSource] = useState("all");
  const [pagination, setPagination] = useState({ key: "", count: PAGE_SIZE });
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);

  useEffect(() => {
    fetch(DATASET_URL)
      .then((response) => {
        if (!response.ok) throw new Error(`Dataset request failed (${response.status})`);
        return response.json();
      })
      .then((value: Dataset) => setDataset(value))
      .catch((error: Error) => setLoadError(error.message));
  }, []);

  const months = useMemo(() => {
    if (!dataset) return [];
    return [...new Set(dataset.events.map(monthKey))].sort();
  }, [dataset]);

  const organizations = useMemo(() => {
    if (!dataset) return [];
    return [...new Set(dataset.events.flatMap(eventOrganizations))].sort();
  }, [dataset]);

  const sources = useMemo(() => {
    if (!dataset) return [];
    return [...new Set(dataset.events.map((event) => event.source_calendar.feed_source))].sort();
  }, [dataset]);

  const filteredEvents = useMemo(() => {
    if (!dataset) return [];
    const normalizedQuery = query.trim().toLocaleLowerCase();
    return dataset.events.filter((event) => {
      const matchesSearch = !normalizedQuery || [
        event.title,
        event.description_text,
        event.location,
        event.source_calendar.calendar_name,
        ...eventOrganizations(event),
      ].join(" ").toLocaleLowerCase().includes(normalizedQuery);
      const matchesMonth = month === "all" || monthKey(event) === month;
      const matchesOrganization = organization === "all" || eventOrganizations(event).includes(organization);
      const matchesTiming = timing === "all" || (timing === "all-day" ? event.all_day : !event.all_day);
      const matchesSource = source === "all" || event.source_calendar.feed_source === source;
      return matchesSearch && matchesMonth && matchesOrganization && matchesTiming && matchesSource;
    });
  }, [dataset, month, organization, query, source, timing]);

  const filterKey = `${query}\u0000${month}\u0000${organization}\u0000${timing}\u0000${source}`;
  const visibleCount = pagination.key === filterKey ? pagination.count : PAGE_SIZE;
  const visibleEvents = filteredEvents.slice(0, visibleCount);
  const eventGroups = useMemo(() => {
    return visibleEvents.reduce<Record<string, CalendarEvent[]>>((groups, event) => {
      const key = dateKey(event);
      (groups[key] ??= []).push(event);
      return groups;
    }, {});
  }, [visibleEvents]);

  const resetFilters = () => {
    setQuery("");
    setMonth("all");
    setOrganization("all");
    setTiming("all");
    setSource("all");
  };

  if (loadError) {
    return <main className="state-page"><p className="eyebrow">Calendar unavailable</p><h1>We couldn’t load the event dataset.</h1><p>{loadError}</p></main>;
  }

  if (!dataset) {
    return <main className="state-page loading-state"><span className="loading-mark">CV</span><p>Gathering the district calendar…</p></main>;
  }

  const generatedDate = new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(new Date(dataset.metadata.generated_at));
  const activeFilters = [month, organization, timing, source].filter((value) => value !== "all").length + (query ? 1 : 0);

  return (
    <main>
      <header className="site-header">
        <a className="wordmark" href="#top" aria-label="CVUSD Calendar Atlas home"><span>CV</span><strong>Calendar Atlas</strong></a>
        <p>Community index · Official public sources</p>
        <a className="header-link" href="#explore">Explore dates <Icon name="arrow" /></a>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">Castro Valley Unified School District</p>
          <h1>One district.<br /><em>Every public date.</em></h1>
          <p className="hero-lede">A searchable, source-linked view of twelve months of school events—assembled from every public district and campus calendar we could find.</p>
        </div>
        <div className="hero-proof" aria-label="Dataset summary">
          <div><strong>{dataset.metadata.event_count.toLocaleString()}</strong><span>events</span></div>
          <div><strong>{dataset.metadata.publication_calendar_count}</strong><span>published calendars</span></div>
          <div><strong>{dataset.metadata.official_organization_count}</strong><span>official organizations checked</span></div>
          <p><span className="status-dot" /> Last rebuilt {generatedDate} · {dataset.metadata.source_error_count} source errors</p>
        </div>
      </section>

      <section className="explorer" id="explore">
        <aside className="filter-panel">
          <div className="filter-heading">
            <div><p className="eyebrow">Refine</p><h2>Find your dates</h2></div>
            {activeFilters > 0 && <button type="button" onClick={resetFilters}>Clear {activeFilters}</button>}
          </div>

          <label className="search-box">
            <span className="sr-only">Search events</span>
            <Icon name="search" />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search events, places…" />
          </label>

          <label className="field-label" htmlFor="organization">School or organization</label>
          <select id="organization" value={organization} onChange={(event) => setOrganization(event.target.value)}>
            <option value="all">All organizations</option>
            {organizations.map((name) => <option key={name} value={name}>{name}</option>)}
          </select>

          <fieldset>
            <legend>Time</legend>
            <div className="segmented-control">
              {[['all', 'Any'], ['all-day', 'All day'], ['timed', 'Timed']].map(([value, label]) => (
                <button type="button" className={timing === value ? "active" : ""} onClick={() => setTiming(value)} key={value}>{label}</button>
              ))}
            </div>
          </fieldset>

          <label className="field-label" htmlFor="source">Source format</label>
          <select id="source" value={source} onChange={(event) => setSource(event.target.value)}>
            <option value="all">All source formats</option>
            {sources.map((value) => <option key={value} value={value}>{sourceLabel(value)}</option>)}
          </select>

          <div className="coverage-note">
            <span>{dataset.metadata.exact_duplicate_records_removed.toLocaleString()}</span>
            <p>duplicate publications reconciled into one cleaner timeline.</p>
          </div>
        </aside>

        <div className="event-browser">
          <div className="month-strip" aria-label="Filter by month">
            <button type="button" className={month === "all" ? "active" : ""} onClick={() => setMonth("all")}>All dates</button>
            {months.map((value) => <button type="button" className={month === value ? "active" : ""} onClick={() => setMonth(value)} key={value}>{formatMonth(value)}</button>)}
          </div>

          <div className="results-header">
            <div><p className="eyebrow">Agenda</p><h2>{filteredEvents.length.toLocaleString()} {filteredEvents.length === 1 ? "event" : "events"}</h2></div>
            <p>{dataset.metadata.window_start} <span>→</span> {dataset.metadata.window_end_inclusive}</p>
          </div>

          {filteredEvents.length === 0 ? (
            <div className="empty-state"><span>0</span><h3>No dates match this combination.</h3><p>Try a broader search or clear the filters.</p><button type="button" onClick={resetFilters}>Show every event</button></div>
          ) : (
            <div className="agenda">
              {Object.entries(eventGroups).map(([day, events]) => (
                <section className="day-group" key={day}>
                  <div className="day-heading"><time dateTime={day}>{formatDay(day)}</time><span>{events.length}</span></div>
                  <div className="day-events">
                    {events.map((event) => {
                      const orgs = eventOrganizations(event);
                      return (
                        <button className="event-card" type="button" onClick={() => setSelectedEvent(event)} key={event.id}>
                          <span className={`event-time ${event.all_day ? "all-day" : ""}`}>{event.all_day ? "ALL DAY" : formatTime(event.start)}</span>
                          <span className="event-main">
                            <strong>{event.title}</strong>
                            <span className="event-meta">{orgs[0]}{orgs.length > 1 ? ` +${orgs.length - 1}` : ""}{event.location ? ` · ${event.location}` : ""}</span>
                          </span>
                          <span className="source-tag">{sourceLabel(event.source_calendar.feed_source)}</span>
                          <span className="event-arrow"><Icon name="arrow" /></span>
                        </button>
                      );
                    })}
                  </div>
                </section>
              ))}
              {visibleCount < filteredEvents.length && <button className="load-more" type="button" onClick={() => setPagination({ key: filterKey, count: visibleCount + PAGE_SIZE })}>Show {Math.min(PAGE_SIZE, filteredEvents.length - visibleCount)} more events</button>}
            </div>
          )}
        </div>
      </section>

      <footer>
        <div><span className="footer-mark">CV</span><p><strong>CVUSD Calendar Atlas</strong><br />A community-built index of official public calendars.</p></div>
        <p>Not an official district service. Dates may change—follow each event’s source link for confirmation.</p>
      </footer>

      {selectedEvent && <EventDetails event={selectedEvent} onClose={() => setSelectedEvent(null)} />}
    </main>
  );
}
