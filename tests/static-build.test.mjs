import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import test from "node:test";

test("builds a static canonical CVUSD application shell", async () => {
  const [html, assets] = await Promise.all([
    readFile(new URL("../dist/index.html", import.meta.url), "utf8"),
    readdir(new URL("../dist/assets/", import.meta.url)),
  ]);

  assert.match(html, /<title>CVUSD Calendar Atlas<\/title>/i);
  assert.match(html, /https:\/\/cvusd\.dooley\.world\//i);
  assert.match(html, /Gathering the district calendar/i);
  assert.match(html, /https:\/\/cvusd\.dooley\.world\/og\.png/i);
  assert.doesNotMatch(html, /chatgpt\.site|codex-preview|vinext|react-loading-skeleton/i);
  assert.ok(assets.some((name) => /^index-.*\.js$/.test(name)));
  assert.ok(assets.some((name) => /^index-.*\.css$/.test(name)));
});

test("keeps the production filters and accessible modal behavior", async () => {
  const [explorer, packageJson, firebaseConfig] = await Promise.all([
    readFile(new URL("../src/CalendarExplorer.tsx", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
    readFile(new URL("../firebase.json", import.meta.url), "utf8"),
  ]);

  assert.match(explorer, /Days of the week/);
  assert.match(explorer, /School level/);
  assert.match(explorer, /Districtwide/);
  assert.match(explorer, /Adult & transition/);
  assert.match(explorer, /Start time/);
  assert.match(explorer, /After 4 PM/);
  assert.match(explorer, /type="range"/);
  assert.match(explorer, /aria-modal="true"/);
  assert.match(explorer, /returnFocus\?\.focus\(\)/);
  assert.match(explorer, /keyEvent\.key !== "Tab"/);
  assert.doesNotMatch(packageJson, /vinext|next|drizzle|wrangler|tailwind/);
  assert.match(firebaseConfig, /"public": "dist"/);
});
