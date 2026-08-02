#!/usr/bin/env python3
"""Discover CVUSD public calendars and build a normalized 12-month JSON dataset."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time as datetime_time, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, unquote, urljoin, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from dateutil import parser as date_parser
from dateutil.rrule import rrulestr


DISTRICT_NAME = "Castro Valley Unified School District"
DEFAULT_TIMEZONE = "America/Los_Angeles"
USER_AGENT = "cvusd-calendar-dataset/1.0 (+public calendar research)"

OFFICIAL_ORGANIZATIONS = [
    ("Castro Valley Unified School District", "https://www.cv.k12.ca.us/"),
    ("Castro Valley Adult and Career Education", "https://www.cvadult.org/"),
    ("Alma State Preschool", "https://alma.cv.k12.ca.us/"),
    ("Castro Valley Elementary School", "https://cve.cv.k12.ca.us/"),
    ("Chabot Elementary School", "https://chabot.cv.k12.ca.us/"),
    ("Independent Elementary School", "https://independent.cv.k12.ca.us/"),
    ("Jensen Ranch Elementary School", "https://jensenranch.cv.k12.ca.us/"),
    ("Marshall Elementary School", "https://marshall.cv.k12.ca.us/"),
    ("Palomares Elementary School", "https://palomares.cv.k12.ca.us/"),
    ("Proctor Elementary School", "https://proctor.cv.k12.ca.us/"),
    ("Stanton Elementary School", "https://stanton.cv.k12.ca.us/"),
    ("Vannoy Elementary School", "https://vannoy.cv.k12.ca.us/"),
    ("Canyon Middle School", "https://canyon.cv.k12.ca.us/"),
    ("Creekside Middle School", "https://creekside.cv.k12.ca.us/"),
    ("Castro Valley High School", "https://cvhs.cv.k12.ca.us/"),
    ("Redwood High School", "https://redwood.cv.k12.ca.us/"),
    ("Castro Valley Virtual Academy 9-12", "https://virtualacademy.cv.k12.ca.us/"),
    ("Roy Johnson Adult Transition", "https://royjohnson.cv.k12.ca.us/"),
]

INSTRUCTIONAL_PDF_URL = (
    "https://files.smartsites.parentsquare.com/8941/"
    "cvusd_calendar_-_2026-27_approved_20251022.pdf"
)
INSTRUCTIONAL_PAGE_URL = "https://www.cv.k12.ca.us/district-instructional-calendar"
ATHLETICS_CALENDAR_URL = "https://sites.google.com/cv.k12.ca.us/cvhsathletics/calendar"


def all_day_event(
    event_id: str,
    title: str,
    start: str,
    end_inclusive: str | None = None,
    description: str = "",
) -> dict[str, Any]:
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end_inclusive or start) + timedelta(days=1)
    return {
        "id": event_id,
        "title": title,
        "start_datetime": start_date.isoformat(),
        "end_datetime": end_date.isoformat(),
        "timezone": DEFAULT_TIMEZONE,
        "all_day": True,
        "description": description,
        "address": "",
    }


INSTRUCTIONAL_CALENDAR_EVENTS = [
    all_day_event("staff-development-2026-08-03", "Staff Development Day (No School)", "2026-08-03"),
    all_day_event("certificated-work-day-2026-08-04", "Certificated Work Day", "2026-08-04"),
    all_day_event("first-day-2026-08-05", "First Day of School", "2026-08-05"),
    all_day_event("student-advisement-2026-09-25", "Student Advisement Conference (No School Pre-5)", "2026-09-25"),
    all_day_event("staff-development-2026-10-13", "Staff Development Day (No School)", "2026-10-13"),
    all_day_event(
        "certificated-work-day-2027-01-04",
        "6-12 Certificated Work Day (No School 6-12)",
        "2027-01-04",
        description="January 4, 2027 is a school day for preschool through grade 5 students.",
    ),
    all_day_event("last-day-2027-05-28", "Last Day of School", "2027-05-28"),
    all_day_event("certificated-work-day-2027-06-01", "Certificated Work Day", "2027-06-01"),
    all_day_event("minimum-pre5-2026-09-22", "District-Wide Minimum Days (Pre-5)", "2026-09-22", "2026-09-24"),
    all_day_event("minimum-pre5-2026-11-10", "District-Wide Minimum Day (Pre-5)", "2026-11-10"),
    all_day_event("minimum-pre5-2026-11-12", "District-Wide Minimum Day (Pre-5)", "2026-11-12"),
    all_day_event("minimum-pre5-2027-03-03", "District-Wide Minimum Day (Pre-5)", "2027-03-03"),
    all_day_event("minimum-pre5-2027-03-04", "District-Wide Minimum Day (Pre-5)", "2027-03-04"),
    all_day_event("minimum-pre5-2027-03-24", "District-Wide Minimum Day (Pre-5)", "2027-03-24"),
    all_day_event("minimum-pre5-2027-03-25", "District-Wide Minimum Day (Pre-5)", "2027-03-25"),
    all_day_event("minimum-pre5-2027-05-28", "District-Wide Minimum Day (Pre-5)", "2027-05-28"),
    all_day_event("minimum-6-8-2026-10-06", "District-Wide Minimum Day (Grades 6-8)", "2026-10-06"),
    all_day_event("minimum-6-8-2026-10-08", "District-Wide Minimum Day (Grades 6-8)", "2026-10-08"),
    all_day_event("minimum-6-8-2026-12-17", "District-Wide Minimum Day (Grades 6-8)", "2026-12-17"),
    all_day_event("minimum-6-8-2026-12-18", "District-Wide Minimum Day (Grades 6-8)", "2026-12-18"),
    all_day_event("minimum-6-8-2027-03-18", "District-Wide Minimum Day (Grades 6-8)", "2027-03-18"),
    all_day_event("minimum-6-8-2027-03-19", "District-Wide Minimum Day (Grades 6-8)", "2027-03-19"),
    all_day_event("minimum-6-8-2027-05-26", "District-Wide Minimum Days (Grades 6-8)", "2027-05-26", "2027-05-28"),
    all_day_event("minimum-9-12-2026-12-16", "District-Wide Minimum Days (Grades 9-12)", "2026-12-16", "2026-12-18"),
    all_day_event("minimum-9-12-2027-05-26", "District-Wide Minimum Days (Grades 9-12)", "2027-05-26", "2027-05-28"),
    all_day_event("labor-day-2026", "Labor Day (No School)", "2026-09-07"),
    all_day_event("fall-non-school-2026-10-09", "Fall Non-School Day", "2026-10-09"),
    all_day_event("fall-non-school-2026-10-12", "Fall Non-School Day", "2026-10-12"),
    all_day_event("veterans-day-2026", "Veterans Day (No School)", "2026-11-11"),
    all_day_event("thanksgiving-break-2026", "Thanksgiving Break", "2026-11-23", "2026-11-27"),
    all_day_event("winter-break-2026", "Winter Break", "2026-12-21", "2027-01-01"),
    all_day_event("mlk-day-2027", "Martin Luther King Jr. Birthday (No School)", "2027-01-18"),
    all_day_event("presidents-break-2027", "President's Day Break", "2027-02-15", "2027-02-19"),
    all_day_event("spring-break-2027", "Spring Break/Cesar Chavez Holiday", "2027-03-29", "2027-04-02"),
    all_day_event("spring-non-school-2027", "Spring Non-School Day", "2027-04-26"),
    all_day_event("memorial-day-2027", "Memorial Day (No School)", "2027-05-31"),
    all_day_event("juneteenth-2027", "Juneteenth", "2027-06-18"),
    all_day_event("secondary-quarter-1-2026", "End of 1st Quarter", "2026-10-08"),
    all_day_event("secondary-semester-1-2026", "End of 1st Semester / 2nd Quarter (88 days)", "2026-12-18"),
    all_day_event("secondary-quarter-3-2027", "End of 3rd Quarter", "2027-03-19"),
    all_day_event("secondary-semester-2-2027", "End of 2nd Semester / 4th Quarter (92 days)", "2027-05-28"),
    all_day_event("elementary-trimester-1-2026", "Elementary: End of Trimester 1", "2026-11-03"),
    all_day_event("elementary-progress-1-2026", "Elementary: Trimester 1 Progress Reports", "2026-09-25"),
    all_day_event("elementary-report-1-2026", "Elementary: Trimester 1 Report Cards", "2026-11-20"),
    all_day_event("elementary-trimester-2-2027", "Elementary: End of Trimester 2", "2027-02-25"),
    all_day_event("elementary-progress-2-2027", "Elementary: Trimester 2 Progress Reports", "2027-01-08"),
    all_day_event("elementary-report-2-2027", "Elementary: Trimester 2 Report Cards", "2027-03-12"),
    all_day_event("elementary-trimester-3-2027", "Elementary: End of Trimester 3", "2027-05-28"),
    all_day_event("elementary-progress-3-2027", "Elementary: Trimester 3 Progress Reports", "2027-04-16"),
    all_day_event("elementary-report-3-2027", "Elementary: Trimester 3 Report Cards", "2027-05-28"),
]

ATHLETICS_BOOSTER_EVENTS = [
    ("2026-08-19", "CVHS Cafeteria"),
    ("2026-09-30", "CVHS Library"),
    ("2026-11-12", "CVHS Cafeteria"),
    ("2027-01-13", "CVHS Library"),
    ("2027-02-24", "CVHS Cafeteria"),
    ("2027-03-24", "CVHS Library"),
    ("2027-05-12", "CVHS Library"),
]


def eprint(*values: object) -> None:
    print(*values, file=sys.stderr, flush=True)


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_text(url: str, accept: str = "text/html,*/*", retries: int = 3) -> str:
    request = Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": USER_AGENT,
            "Referer": f"{urlparse(url).scheme}://{urlparse(url).netloc}/",
        },
    )
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urlopen(request, timeout=30) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return response.read().decode(charset, errors="replace")
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(0.5 * (attempt + 1))
    assert last_error is not None
    raise last_error


class CalendarHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict[str, str]] = []
        self.iframes: list[str] = []
        self.json_scripts: list[tuple[dict[str, str], str]] = []
        self._anchor: dict[str, Any] | None = None
        self._script_attrs: dict[str, str] | None = None
        self._script_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if tag == "a" and attr_map.get("href"):
            self._anchor = {"href": attr_map["href"], "text": []}
        elif tag == "iframe" and attr_map.get("src"):
            self.iframes.append(attr_map["src"])
        elif tag == "script" and attr_map.get("type") == "application/json":
            self._script_attrs = attr_map
            self._script_text = []

    def handle_data(self, data: str) -> None:
        if self._anchor is not None:
            self._anchor["text"].append(data)
        if self._script_attrs is not None:
            self._script_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._anchor is not None:
            self.links.append(
                {
                    "href": self._anchor["href"],
                    "text": " ".join("".join(self._anchor["text"]).split()),
                }
            )
            self._anchor = None
        elif tag == "script" and self._script_attrs is not None:
            self.json_scripts.append((self._script_attrs, "".join(self._script_text)))
            self._script_attrs = None
            self._script_text = []


def parse_html(text: str) -> CalendarHtmlParser:
    parser = CalendarHtmlParser()
    parser.feed(text)
    return parser


def clean_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed._replace(fragment="").geturl()


def calendarish_link(text: str, href: str) -> bool:
    value = f"{text} {href}".lower()
    if any(
        term in value
        for term in (
            "instructional-calendar",
            "instructional calendar",
            "classified work year",
            "work-year",
            "work_calendar",
            "bell schedule",
            "schedule change",
        )
    ):
        return False
    return "calendar" in value


def normalized_hostname(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def extract_google_calendar_ids(iframe_url: str) -> list[str]:
    if "calendar.google.com" not in iframe_url:
        return []
    values = parse_qs(urlparse(iframe_url).query).get("src", [])
    return [unquote(value) for value in values if "@" in unquote(value)]


def smartsite_configs(text: str) -> list[dict[str, Any]]:
    parser = parse_html(text)
    configs: list[dict[str, Any]] = []
    for attrs, payload in parser.json_scripts:
        if not any(key.startswith("data-view-data-events-sliders") for key in attrs):
            continue
        try:
            item = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict) and item.get("calendarApiID"):
            configs.append(item)
    return configs


@dataclass(frozen=True)
class CandidatePage:
    organization: str
    site_url: str
    url: str
    link_text: str


def discover_calendars() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    discoveries: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    visited_pages: set[str] = set()

    for organization, site_url in OFFICIAL_ORGANIZATIONS:
        eprint(f"Discovering: {organization}")
        candidates: dict[str, CandidatePage] = {}
        discovery_urls = [site_url]
        if urlparse(site_url).hostname and urlparse(site_url).hostname.endswith("cv.k12.ca.us"):
            discovery_urls.append(urljoin(site_url, "/site_map"))

        for discovery_url in discovery_urls:
            try:
                text = fetch_text(discovery_url)
            except Exception as exc:  # noqa: BLE001
                errors.append({"stage": "discovery", "organization": organization, "url": discovery_url, "error": str(exc)})
                continue
            parser = parse_html(text)
            for link in parser.links:
                href = clean_url(urljoin(discovery_url, link["href"]))
                if not href.startswith(("http://", "https://")):
                    continue
                if calendarish_link(link["text"], href):
                    candidates[href] = CandidatePage(organization, site_url, href, link["text"])

            # A calendar component can also appear directly on a home page.
            if smartsite_configs(text) or any(extract_google_calendar_ids(src) for src in parser.iframes):
                candidates[discovery_url] = CandidatePage(organization, site_url, discovery_url, "Embedded calendar")

        # The site navigation sometimes exposes no text calendar link but uses the standard route.
        # Only add the standard route after an official CVUSD page has confirmed SmartSites markup.
        if not candidates and urlparse(site_url).hostname and urlparse(site_url).hostname.endswith("cv.k12.ca.us"):
            candidates[urljoin(site_url, "/calendar")] = CandidatePage(organization, site_url, urljoin(site_url, "/calendar"), "Calendar")

        for candidate in sorted(candidates.values(), key=lambda value: value.url):
            if candidate.url in visited_pages:
                continue
            visited_pages.add(candidate.url)
            try:
                text = fetch_text(candidate.url)
            except Exception as exc:  # noqa: BLE001
                errors.append({"stage": "calendar_page", "organization": organization, "url": candidate.url, "error": str(exc)})
                continue

            parser = parse_html(text)
            configs = smartsite_configs(text)
            google_ids = sorted({calendar_id for src in parser.iframes for calendar_id in extract_google_calendar_ids(src)})
            external_links = []
            for link in parser.links:
                href = clean_url(urljoin(candidate.url, link["href"]))
                if not href.startswith(("http://", "https://")):
                    continue
                if calendarish_link(link["text"], href) and normalized_hostname(href) != normalized_hostname(candidate.site_url):
                    external_links.append({"text": link["text"], "url": href})

            if configs or google_ids or external_links:
                discoveries.append(
                    {
                        "organization": candidate.organization,
                        "organization_site_url": candidate.site_url,
                        "calendar_page_url": candidate.url,
                        "link_text": candidate.link_text,
                        "smartsite_calendars": [
                            {
                                "calendar_api_id": int(config["calendarApiID"]),
                                "calendar_internal_id": config.get("calendarID"),
                                "title": config.get("componentTitle") or "Calendar",
                                "calendar_link": urljoin(candidate.url, config.get("calendarLink") or ""),
                                "is_meal_calendar": bool(config.get("isMealCalendar")),
                            }
                            for config in configs
                        ],
                        "google_calendar_ids": google_ids,
                        "external_calendar_links": sorted(external_links, key=lambda value: (value["url"], value["text"])),
                    }
                )

    return discoveries, errors


def iter_month_intervals(start: date, end_exclusive: date) -> Iterable[tuple[date, date]]:
    cursor = start
    while cursor < end_exclusive:
        if cursor.month == 12:
            next_month = date(cursor.year + 1, 1, 1)
        else:
            next_month = date(cursor.year, cursor.month + 1, 1)
        interval_end = min(next_month, end_exclusive)
        yield cursor, interval_end
        cursor = interval_end


def fetch_smartsite_events(
    calendar: dict[str, Any], start: date, end_exclusive: date
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    base_url = calendar["api_origin"]
    calendar_id = calendar["calendar_api_id"]
    for interval_start, interval_end in iter_month_intervals(start, end_exclusive):
        endpoint = (
            f"{base_url}/api/calendars/{calendar_id}/events"
            f"?start_date={interval_start.isoformat()}&end_date={interval_end.isoformat()}&view_source=full-calendar"
        )
        try:
            payload = json.loads(fetch_text(endpoint, accept="application/json"))
            if not payload.get("success") or payload.get("data", {}).get("error"):
                raise ValueError(payload.get("data", {}).get("error") or payload.get("error") or "API returned unsuccessful response")
            site_timezone = payload.get("data", {}).get("site_timezone") or DEFAULT_TIMEZONE
            for item in payload.get("data", {}).get("events", []):
                if isinstance(item, dict):
                    record = dict(item)
                    record["_site_timezone"] = site_timezone
                    record["_endpoint"] = endpoint
                    events.append(record)
        except Exception as exc:  # noqa: BLE001
            errors.append(
                {
                    "stage": "events_api",
                    "organization": calendar["organization"],
                    "calendar_api_id": calendar_id,
                    "url": endpoint,
                    "error": str(exc),
                }
            )
    return events, errors


def unfold_ics(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines: list[str] = []
    for line in normalized.split("\n"):
        if line.startswith((" ", "\t")) and lines:
            lines[-1] += line[1:]
        else:
            lines.append(line)
    return lines


def unescape_ics(value: str) -> str:
    return (
        value.replace("\\N", "\n")
        .replace("\\n", "\n")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
    )


def parse_ics_property(line: str) -> tuple[str, dict[str, str], str]:
    head, _, value = line.partition(":")
    pieces = head.split(";")
    name = pieces[0].upper()
    params = {}
    for piece in pieces[1:]:
        key, sep, param_value = piece.partition("=")
        if sep:
            params[key.upper()] = param_value.strip('"')
    return name, params, unescape_ics(value)


def parse_ics_datetime(value: str, params: dict[str, str]) -> tuple[date | datetime, bool]:
    is_date = params.get("VALUE", "").upper() == "DATE" or bool(re.fullmatch(r"\d{8}", value))
    if is_date:
        return datetime.strptime(value[:8], "%Y%m%d").date(), True
    if value.endswith("Z"):
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc), False
    parsed = datetime.strptime(value, "%Y%m%dT%H%M%S")
    tzid = params.get("TZID")
    try:
        zone = ZoneInfo(tzid) if tzid else ZoneInfo(DEFAULT_TIMEZONE)
    except Exception:  # noqa: BLE001
        zone = ZoneInfo(DEFAULT_TIMEZONE)
    return parsed.replace(tzinfo=zone), False


def iso_event_value(value: date | datetime, all_day: bool) -> str:
    if all_day:
        assert isinstance(value, date)
        return value.isoformat()
    assert isinstance(value, datetime)
    return value.isoformat()


def parse_google_ics_events(
    calendar_id: str, organization: str, page_url: str, start: date, end_exclusive: date
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ics_url = f"https://calendar.google.com/calendar/ical/{quote(calendar_id, safe='')}/public/basic.ics"
    try:
        text = fetch_text(ics_url, accept="text/calendar,*/*")
    except Exception as exc:  # noqa: BLE001
        return [], [{"stage": "google_ics", "organization": organization, "url": ics_url, "error": str(exc)}]

    raw_events: list[dict[str, list[tuple[dict[str, str], str]]]] = []
    current: dict[str, list[tuple[dict[str, str], str]]] | None = None
    for line in unfold_ics(text):
        if line == "BEGIN:VEVENT":
            current = defaultdict(list)
        elif line == "END:VEVENT" and current is not None:
            raw_events.append(dict(current))
            current = None
        elif current is not None and ":" in line:
            name, params, value = parse_ics_property(line)
            current[name].append((params, value))

    window_start_dt = datetime.combine(start, datetime_time.min, ZoneInfo(DEFAULT_TIMEZONE))
    window_end_dt = datetime.combine(end_exclusive, datetime_time.min, ZoneInfo(DEFAULT_TIMEZONE))
    output: list[dict[str, Any]] = []

    for raw in raw_events:
        if "DTSTART" not in raw:
            continue
        start_value, all_day = parse_ics_datetime(raw["DTSTART"][0][1], raw["DTSTART"][0][0])
        if "DTEND" in raw:
            end_value, _ = parse_ics_datetime(raw["DTEND"][0][1], raw["DTEND"][0][0])
        else:
            end_value = start_value + (timedelta(days=1) if all_day else timedelta(0))

        start_dt = datetime.combine(start_value, datetime_time.min, ZoneInfo(DEFAULT_TIMEZONE)) if all_day else start_value
        end_dt = datetime.combine(end_value, datetime_time.min, ZoneInfo(DEFAULT_TIMEZONE)) if all_day else end_value
        assert isinstance(start_dt, datetime) and isinstance(end_dt, datetime)
        duration = end_dt - start_dt
        starts = [start_dt]

        if raw.get("RRULE"):
            rule_text = raw["RRULE"][0][1]
            try:
                rule = rrulestr(rule_text, dtstart=start_dt)
                starts = list(rule.between(window_start_dt - duration, window_end_dt, inc=True))
            except Exception as exc:  # noqa: BLE001
                if "UNTIL values must be specified in UTC" in str(exc):
                    # Some Google exports contain a local (non-Z) UNTIL even
                    # though DTSTART is timezone-aware. Expand in local wall
                    # time, then restore the DTSTART zone.
                    naive_rule = rrulestr(rule_text, dtstart=start_dt.replace(tzinfo=None))
                    naive_starts = naive_rule.between(
                        (window_start_dt - duration).replace(tzinfo=None),
                        window_end_dt.replace(tzinfo=None),
                        inc=True,
                    )
                    starts = [value.replace(tzinfo=start_dt.tzinfo) for value in naive_starts]
                else:
                    eprint(f"Warning: could not expand RRULE for {calendar_id}: {exc}")
        excluded: set[datetime] = set()
        for params, value in raw.get("EXDATE", []):
            for piece in value.split(","):
                excluded_value, excluded_all_day = parse_ics_datetime(piece, params)
                excluded_dt = (
                    datetime.combine(excluded_value, datetime_time.min, ZoneInfo(DEFAULT_TIMEZONE))
                    if excluded_all_day
                    else excluded_value
                )
                assert isinstance(excluded_dt, datetime)
                excluded.add(excluded_dt)

        uid = raw.get("UID", [({}, "")])[0][1]
        title = raw.get("SUMMARY", [({}, "")])[0][1]
        description = raw.get("DESCRIPTION", [({}, "")])[0][1]
        location = raw.get("LOCATION", [({}, "")])[0][1]
        event_url = raw.get("URL", [({}, "")])[0][1]
        for occurrence_start in starts:
            if occurrence_start in excluded:
                continue
            occurrence_end = occurrence_start + duration
            if not (occurrence_start < window_end_dt and occurrence_end > window_start_dt):
                continue
            if all_day:
                occurrence_start_value: date | datetime = occurrence_start.date()
                occurrence_end_value: date | datetime = occurrence_end.date()
            else:
                occurrence_start_value = occurrence_start.astimezone(ZoneInfo(DEFAULT_TIMEZONE))
                occurrence_end_value = occurrence_end.astimezone(ZoneInfo(DEFAULT_TIMEZONE))
            output.append(
                {
                    "id": uid,
                    "title": title,
                    "start_datetime": iso_event_value(occurrence_start_value, all_day),
                    "end_datetime": iso_event_value(occurrence_end_value, all_day),
                    "timezone": DEFAULT_TIMEZONE,
                    "all_day": all_day,
                    "description": description,
                    "address": location,
                    "event_url": event_url,
                    "calendar_id": calendar_id,
                    "calendar_name": raw.get("X-WR-CALNAME", [({}, "Google Calendar")])[0][1],
                    "feed_id": calendar_id,
                    "feed_source": "google_ics",
                    "_site_timezone": DEFAULT_TIMEZONE,
                    "_endpoint": ics_url,
                    "_organization": organization,
                    "_calendar_page_url": page_url,
                }
            )
    return output, []


def strip_html(value: str) -> str:
    if not value:
        return ""
    text = re.sub(r"<\s*br\s*/?\s*>", "\n", value, flags=re.IGNORECASE)
    text = re.sub(r"</\s*(p|div|li)\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return "\n".join(line.strip() for line in html.unescape(text).splitlines() if line.strip())


def parse_boundary(value: str, all_day: bool, fallback_zone: str) -> datetime:
    if all_day and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return datetime.combine(date.fromisoformat(value), datetime_time.min, ZoneInfo(fallback_zone))
    parsed = date_parser.isoparse(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo(fallback_zone))
    return parsed


def normalize_event(
    raw: dict[str, Any], publication: dict[str, Any], window_start: date, window_end_exclusive: date
) -> dict[str, Any] | None:
    all_day = bool(raw.get("all_day"))
    site_timezone = raw.get("timezone") or raw.get("_site_timezone") or DEFAULT_TIMEZONE
    start_value = raw.get("start_datetime") or raw.get("start_date")
    end_value = raw.get("end_datetime") or raw.get("end_date") or start_value
    if not start_value or not end_value:
        return None
    start_dt = parse_boundary(str(start_value), all_day, site_timezone)
    end_dt = parse_boundary(str(end_value), all_day, site_timezone)
    if all_day and end_dt <= start_dt:
        # SmartSites represents some one-day all-day events with identical
        # start/end dates. Normalize them to FullCalendar/ICS exclusive-end
        # semantics so every all-day interval has a positive duration.
        end_dt = start_dt + timedelta(days=1)
        end_value = end_dt.date().isoformat()
    window_start_dt = datetime.combine(window_start, datetime_time.min, ZoneInfo(DEFAULT_TIMEZONE))
    window_end_dt = datetime.combine(window_end_exclusive, datetime_time.min, ZoneInfo(DEFAULT_TIMEZONE))
    if not (start_dt < window_end_dt and end_dt > window_start_dt):
        return None

    source_id = str(raw.get("id") or "")
    feed_source = str(raw.get("feed_source") or publication["platform"])
    feed_id = str(raw.get("feed_id") or raw.get("calendar_id") or publication["calendar_key"])
    calendar_id = str(raw.get("calendar_id") or publication["calendar_key"])
    if feed_source.startswith("google"):
        # The same public Google event is often exposed both through a school's
        # iframe/ICS feed and through its SmartSites aggregate API.
        canonical_source_id = re.sub(r"@google\.com$", "", source_id, flags=re.IGNORECASE)
        if all_day:
            canonical_start = start_dt.date().isoformat()
            canonical_end = end_dt.date().isoformat()
        else:
            canonical_start = start_dt.astimezone(timezone.utc).isoformat()
            canonical_end = end_dt.astimezone(timezone.utc).isoformat()
        dedupe_material = "|".join(["google", canonical_source_id, canonical_start, canonical_end])
    else:
        dedupe_material = "|".join([feed_source, feed_id, source_id, start_dt.isoformat(), end_dt.isoformat()])
    stable_id = hashlib.sha256(dedupe_material.encode("utf-8")).hexdigest()[:24]

    link = str(raw.get("event_url") or raw.get("link") or "")
    if link and link.startswith("/"):
        link = urljoin(publication["api_origin"] + "/", link)
    description_html = str(raw.get("description") or "")
    return {
        "id": stable_id,
        "source_event_id": source_id,
        "title": str(raw.get("title") or "").strip(),
        "start": str(start_value),
        "end": str(end_value),
        "end_time_known": bool(raw.get("_end_time_known", True)),
        "all_day": all_day,
        "timezone": site_timezone,
        "description": description_html,
        "description_text": strip_html(description_html),
        "location": str(raw.get("address") or ""),
        "url": link,
        "source_calendar": {
            "calendar_id": calendar_id,
            "calendar_name": str(raw.get("calendar_name") or publication["name"]),
            "feed_id": feed_id,
            "feed_source": feed_source,
        },
        "published_via": [
            {
                "calendar_key": publication["calendar_key"],
                "organization": publication["organization"],
                "calendar_page_url": publication["calendar_page_url"],
                "endpoint": raw.get("_endpoint") or publication.get("endpoint"),
            }
        ],
    }


def build_publications(discoveries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    publications: dict[tuple[str, str, str], dict[str, Any]] = {}
    for discovery in discoveries:
        page_url = discovery["calendar_page_url"]
        origin = f"{urlparse(page_url).scheme}://{urlparse(page_url).netloc}"
        for calendar in discovery["smartsite_calendars"]:
            key = str(calendar["calendar_api_id"])
            identity = ("smartsites", origin, key)
            publications[identity] = {
                "calendar_key": key,
                "platform": "parentsquare_smartsites",
                "name": calendar["title"],
                "organization": discovery["organization"],
                "organization_site_url": discovery["organization_site_url"],
                "calendar_page_url": page_url,
                "calendar_api_id": calendar["calendar_api_id"],
                "calendar_internal_id": calendar["calendar_internal_id"],
                "api_origin": origin,
                "endpoint_template": f"{origin}/api/calendars/{key}/events?start_date={{start}}&end_date={{end}}&view_source=full-calendar",
                "event_count": 0,
            }
        for google_id in discovery["google_calendar_ids"]:
            identity = ("google_ics", "https://calendar.google.com", google_id)
            publications[identity] = {
                "calendar_key": google_id,
                "platform": "google_ics",
                "name": discovery["link_text"] or "Google Calendar",
                "organization": discovery["organization"],
                "organization_site_url": discovery["organization_site_url"],
                "calendar_page_url": page_url,
                "google_calendar_id": google_id,
                "api_origin": origin,
                "endpoint": f"https://calendar.google.com/calendar/ical/{quote(google_id, safe='')}/public/basic.ics",
                "event_count": 0,
            }
    platform_order = {"parentsquare_smartsites": 0, "google_ics": 1}
    return sorted(
        publications.values(),
        key=lambda value: (value["organization"], platform_order.get(value["platform"], 9), value["calendar_key"]),
    )


def supplemental_publications() -> list[dict[str, Any]]:
    instructional_events = []
    for event in INSTRUCTIONAL_CALENDAR_EVENTS:
        item = dict(event)
        item.update(
            {
                "calendar_id": "instructional-calendar-2026-2027",
                "calendar_name": "CVUSD Instructional Calendar 2026-2027",
                "feed_id": INSTRUCTIONAL_PDF_URL,
                "feed_source": "official_pdf",
                "_site_timezone": DEFAULT_TIMEZONE,
                "_endpoint": INSTRUCTIONAL_PDF_URL,
            }
        )
        instructional_events.append(item)

    athletics_events = []
    for event_date, location in ATHLETICS_BOOSTER_EVENTS:
        start_value = datetime.fromisoformat(f"{event_date}T18:00:00").replace(tzinfo=ZoneInfo(DEFAULT_TIMEZONE))
        athletics_events.append(
            {
                "id": f"athletic-boosters-{event_date}",
                "title": "CVHS Athletic Boosters Parent Meeting",
                "start_datetime": start_value.isoformat(),
                "end_datetime": start_value.isoformat(),
                "timezone": DEFAULT_TIMEZONE,
                "all_day": False,
                "description": "The source publishes a 6:00 PM start time but no end time.",
                "address": location,
                "calendar_id": "cvhs-athletics-calendar",
                "calendar_name": "CVHS Athletics Calendar",
                "feed_id": ATHLETICS_CALENDAR_URL,
                "feed_source": "official_webpage",
                "_site_timezone": DEFAULT_TIMEZONE,
                "_endpoint": ATHLETICS_CALENDAR_URL,
                "_end_time_known": False,
            }
        )

    return [
        {
            "calendar_key": "instructional-calendar-2026-2027",
            "platform": "official_pdf",
            "name": "CVUSD Instructional Calendar 2026-2027",
            "organization": DISTRICT_NAME,
            "organization_site_url": "https://www.cv.k12.ca.us/",
            "calendar_page_url": INSTRUCTIONAL_PAGE_URL,
            "api_origin": "https://www.cv.k12.ca.us",
            "endpoint": INSTRUCTIONAL_PDF_URL,
            "event_count": 0,
            "_embedded_events": instructional_events,
        },
        {
            "calendar_key": "cvhs-athletics-calendar",
            "platform": "official_webpage",
            "name": "CVHS Athletics Calendar",
            "organization": "Castro Valley High School",
            "organization_site_url": "https://cvhs.cv.k12.ca.us/",
            "calendar_page_url": ATHLETICS_CALENDAR_URL,
            "api_origin": "https://sites.google.com",
            "endpoint": ATHLETICS_CALENDAR_URL,
            "event_count": 0,
            "_embedded_events": athletics_events,
        },
    ]


def build_dataset(window_start: date, window_end_inclusive: date) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc)
    window_end_exclusive = window_end_inclusive + timedelta(days=1)
    discoveries, errors = discover_calendars()
    publications = build_publications(discoveries)
    publications.extend(supplemental_publications())

    normalized_by_id: dict[str, dict[str, Any]] = {}
    exact_duplicates_removed = 0
    organizations_with_smartsites = {
        publication["organization"]
        for publication in publications
        if publication["platform"] == "parentsquare_smartsites"
    }
    for publication in publications:
        eprint(f"Fetching: {publication['organization']} [{publication['platform']}:{publication['calendar_key']}]")
        if publication["platform"] == "parentsquare_smartsites":
            raw_events, fetch_errors = fetch_smartsite_events(publication, window_start, window_end_exclusive)
            publication["ingestion_status"] = "ingested"
        elif publication["platform"] in {"official_pdf", "official_webpage"}:
            raw_events, fetch_errors = publication["_embedded_events"], []
            publication["ingestion_status"] = "ingested"
        elif publication["organization"] in organizations_with_smartsites:
            # SmartSites is subscribed to this same Google calendar and returns
            # correctly expanded recurring instances, overrides, and deletions.
            # Keep the ICS calendar in the inventory without unioning recurrence
            # masters that would duplicate the authoritative API instances.
            raw_events, fetch_errors = [], []
            publication["ingestion_status"] = "covered_by_organization_smartsites_api"
        else:
            raw_events, fetch_errors = parse_google_ics_events(
                publication["google_calendar_id"],
                publication["organization"],
                publication["calendar_page_url"],
                window_start,
                window_end_exclusive,
            )
            publication["ingestion_status"] = "ingested"
        errors.extend(fetch_errors)
        publication_seen: set[str] = set()
        for raw in raw_events:
            event = normalize_event(raw, publication, window_start, window_end_exclusive)
            if event is None:
                continue
            event_id = event["id"]
            if event_id in publication_seen:
                exact_duplicates_removed += 1
                continue
            publication_seen.add(event_id)
            if event_id in normalized_by_id:
                exact_duplicates_removed += 1
                existing_publications = normalized_by_id[event_id]["published_via"]
                for item in event["published_via"]:
                    if item not in existing_publications:
                        existing_publications.append(item)
            else:
                normalized_by_id[event_id] = event
        publication["event_count"] = len(publication_seen)
        publication.pop("_embedded_events", None)

    events = sorted(
        normalized_by_id.values(),
        key=lambda value: (value["start"], value["title"].casefold(), value["id"]),
    )
    source_calendar_counts: dict[tuple[str, str, str, str], int] = defaultdict(int)
    for event in events:
        source = event["source_calendar"]
        source_calendar_counts[
            (source["calendar_id"], source["calendar_name"], source["feed_id"], source["feed_source"])
        ] += 1

    source_calendars = [
        {
            "calendar_id": key[0],
            "calendar_name": key[1],
            "feed_id": key[2],
            "feed_source": key[3],
            "event_count": count,
        }
        for key, count in sorted(source_calendar_counts.items())
    ]

    organizations_with_calendar = {publication["organization"] for publication in publications}
    organizations_without_calendar = [
        {"organization": organization, "site_url": site_url}
        for organization, site_url in OFFICIAL_ORGANIZATIONS
        if organization not in organizations_with_calendar
    ]
    external_links = sorted(
        {
            (discovery["organization"], link["text"], link["url"])
            for discovery in discoveries
            for link in discovery["external_calendar_links"]
        }
    )

    return {
        "metadata": {
            "district": DISTRICT_NAME,
            "generated_at": iso_z(generated_at),
            "timezone": DEFAULT_TIMEZONE,
            "window_start": window_start.isoformat(),
            "window_end_inclusive": window_end_inclusive.isoformat(),
            "window_end_exclusive": window_end_exclusive.isoformat(),
            "scope": "Public event calendars linked from the official CVUSD district, school, and program websites.",
            "event_count": len(events),
            "publication_calendar_count": len(publications),
            "source_calendar_count": len(source_calendars),
            "official_organization_count": len(OFFICIAL_ORGANIZATIONS),
            "exact_duplicate_records_removed": exact_duplicates_removed,
            "source_error_count": len(errors),
        },
        "publication_calendars": publications,
        "source_calendars": source_calendars,
        "events": events,
        "reference_calendars": [
            {
                "name": "CVUSD Instructional Calendar 2026-2027",
                "type": "pdf",
                "url": INSTRUCTIONAL_PDF_URL,
                "page_url": INSTRUCTIONAL_PAGE_URL,
                "notes": "The PDF was rendered and visually verified. Its important dates, grade-band minimum days, holidays, and reporting milestones are included as official_pdf event records.",
            },
            {
                "name": "Castro Valley High School Athletics Calendar",
                "type": "external_calendar",
                "url": ATHLETICS_CALENDAR_URL,
                "legacy_url": "https://westalamedacountyconference.org/public/genie/678/school/5/",
                "availability": "Seven published 2026-2027 Athletic Boosters parent meetings are included. The page says home-game dates are coming soon, and the legacy link redirects to a generic Arbiter migration page, so no game feed was available at collection time.",
            },
        ],
        "discovery": {
            "official_organizations": [
                {"organization": organization, "site_url": site_url}
                for organization, site_url in OFFICIAL_ORGANIZATIONS
            ],
            "organizations_without_discovered_event_calendar": organizations_without_calendar,
            "external_calendar_links_not_ingested": [
                {"organization": organization, "text": text, "url": url}
                for organization, text, url in external_links
            ],
            "calendar_pages": discoveries,
            "errors": errors,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2026, 8, 2))
    parser.add_argument("--end", type=date.fromisoformat, default=date(2027, 8, 2), help="Inclusive end date")
    parser.add_argument("--output", type=Path, default=Path("data/cvusd_events_2026-08-02_to_2027-08-02.json"))
    parser.add_argument(
        "--web-output",
        type=Path,
        default=Path("public/data/cvusd_events.json"),
        help="Mirror the completed dataset here for the calendar UI",
    )
    parser.add_argument(
        "--skip-web-output",
        action="store_true",
        help="Do not update the calendar UI's public dataset",
    )
    parser.add_argument("--discover-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.end < args.start:
        raise SystemExit("--end must be on or after --start")
    if args.discover_only:
        discoveries, errors = discover_calendars()
        print(json.dumps({"discoveries": discoveries, "errors": errors}, indent=2, ensure_ascii=False))
        return 0
    dataset = build_dataset(args.start, args.end)
    serialized_dataset = json.dumps(dataset, indent=2, ensure_ascii=False) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized_dataset, encoding="utf-8")
    eprint(f"Wrote {dataset['metadata']['event_count']} events to {args.output}")
    if not args.skip_web_output and args.web_output.resolve() != args.output.resolve():
        args.web_output.parent.mkdir(parents=True, exist_ok=True)
        args.web_output.write_text(serialized_dataset, encoding="utf-8")
        eprint(f"Mirrored dataset to {args.web_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
