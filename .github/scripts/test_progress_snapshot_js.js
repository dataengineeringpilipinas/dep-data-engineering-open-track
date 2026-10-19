const test = require("node:test");
const assert = require("node:assert/strict");

const {
  formatSnapshotStatus,
  parseGeneratedAt,
  snapshotUrl,
  STALE_HOURS,
} = require("../../docs/assets/progress-snapshot.js");

test("snapshotUrl points at the progress-data branch", () => {
  assert.equal(
    snapshotUrl(),
    "https://raw.githubusercontent.com/dataengineeringpilipinas/dep-data-engineering-open-track/progress-data/progress-snapshot.json",
  );
  assert.equal(
    snapshotUrl("owner", "repo", "branch"),
    "https://raw.githubusercontent.com/owner/repo/branch/progress-snapshot.json",
  );
});

test("parseGeneratedAt rejects missing and invalid values", () => {
  assert.equal(parseGeneratedAt(null), null);
  assert.equal(parseGeneratedAt(""), null);
  assert.equal(parseGeneratedAt("not a date"), null);
  assert.equal(
    parseGeneratedAt("2026-10-19T00:00:00Z").toISOString(),
    "2026-10-19T00:00:00.000Z",
  );
});

test("fresh snapshots are not marked stale", () => {
  const status = formatSnapshotStatus(
    "2026-10-19T00:00:00Z",
    Date.parse("2026-10-19T03:00:00Z"),
  );

  assert.equal(status.stale, false);
  assert.match(status.text, /^Snapshot from /);
});

test("snapshots at the stale threshold are flagged", () => {
  const now = Date.parse("2026-10-19T12:00:00Z");
  const status = formatSnapshotStatus("2026-10-19T00:00:00Z", now);

  assert.equal(status.stale, true);
  assert.match(status.text, new RegExp(`${STALE_HOURS}h old`));
  assert.match(status.text, /refresh may be delayed/);
});

test("missing timestamps are surfaced as stale", () => {
  const status = formatSnapshotStatus(null);

  assert.equal(status.stale, true);
  assert.equal(status.text, "Snapshot timestamp unavailable");
});
