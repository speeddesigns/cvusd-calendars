import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import test from "node:test";

const compareCodePoints = (left, right) => (left < right ? -1 : left > right ? 1 : 0);

test("keeps the dated archive and deployable dataset identical and valid", async () => {
  const mirror = await readFile(new URL("../public/data/cvusd_events.json", import.meta.url));
  const archiveNames = (await readdir(new URL("../data/", import.meta.url)))
    .filter((name) => /^cvusd_events_.*\.json$/.test(name));
  assert.ok(archiveNames.length > 0, "expected at least one dated archive");

  const archives = await Promise.all(
    archiveNames.map((name) => readFile(new URL(`../data/${name}`, import.meta.url))),
  );
  assert.ok(archives.some((archive) => archive.equals(mirror)), "no dated archive matches the deployable mirror");

  const dataset = JSON.parse(mirror.toString("utf8"));
  const events = dataset.events;
  assert.equal(dataset.metadata.event_count, events.length);
  assert.equal(new Set(events.map((event) => event.id)).size, events.length);
  assert.equal(dataset.discovery.errors.length, dataset.metadata.source_error_count);

  const windowStart = dataset.metadata.window_start;
  const windowEnd = dataset.metadata.window_end_inclusive;
  for (const event of events) {
    const startDate = event.start.slice(0, 10);
    assert.ok(startDate >= windowStart && startDate <= windowEnd, `${event.id} is outside the collection window`);
    assert.ok(event.source_calendar?.calendar_id, `${event.id} is missing source identity`);
    assert.ok(event.published_via?.length > 0, `${event.id} is missing publication provenance`);
    if (event.all_day) {
      assert.match(event.start, /^\d{4}-\d{2}-\d{2}$/);
      assert.match(event.end, /^\d{4}-\d{2}-\d{2}$/);
      assert.ok(event.end > event.start, `${event.id} has a non-exclusive all-day end`);
    } else {
      assert.match(event.start, /T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$/);
    }
  }

  const sorted = [...events].sort((left, right) => {
    return compareCodePoints(left.start, right.start)
      || compareCodePoints(left.title.toLowerCase(), right.title.toLowerCase())
      || compareCodePoints(left.id, right.id);
  });
  assert.deepEqual(events.map((event) => event.id), sorted.map((event) => event.id));
});
