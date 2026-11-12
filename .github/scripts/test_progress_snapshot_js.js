const test = require("node:test");
const assert = require("node:assert/strict");

const {
  buildCsv,
  buildDashboardQuery,
  csvCell,
  escapeHtml,
  formatSnapshotStatus,
  parseGeneratedAt,
  readDashboardState,
  safeExternalUrl,
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

test("escapeHtml neutralizes issue-form markup", () => {
  assert.equal(
    escapeHtml(`<img src=x onerror="alert('x')">`),
    "&lt;img src=x onerror=&quot;alert(&#39;x&#39;)&quot;&gt;",
  );
  assert.equal(escapeHtml("Ada & Grace"), "Ada &amp; Grace");
});

test("safeExternalUrl only allows http and https links", () => {
  assert.equal(
    safeExternalUrl("https://github.com/Ada/Project"),
    "https://github.com/Ada/Project",
  );
  assert.equal(
    safeExternalUrl("http://example.com/repo"),
    "http://example.com/repo",
  );
  assert.equal(safeExternalUrl("javascript:alert(1)"), "");
  assert.equal(safeExternalUrl("data:text/html,hello"), "");
  assert.equal(safeExternalUrl("not a url"), "");
  assert.equal(safeExternalUrl("—"), "");
});

test("csvCell quotes commas, quotes, and line breaks", () => {
  assert.equal(csvCell("Ada"), "Ada");
  assert.equal(csvCell(`Ada, "Data"`), `"Ada, ""Data"""`);
  assert.equal(csvCell("line one\nline two"), '"line one\nline two"');
});

test("csvCell prevents spreadsheet formula execution", () => {
  assert.equal(csvCell("=SUM(A1)"), "'=SUM(A1)");
  assert.equal(csvCell("+1"), "'+1");
  assert.equal(csvCell("-1"), "'-1");
  assert.equal(csvCell("@cmd"), "'@cmd");
});

test("buildCsv exports the visible issue fields with escaped values", () => {
  const csv = buildCsv([
    {
      _builder: `Ada, "Data"`,
      _cohort: "2026-A",
      _milestone: "M2",
      _status: "passed",
      _isLate: false,
      created_at: "2026-10-01T00:00:00Z",
      updated_at: "2026-10-02T00:00:00Z",
      _repoUrl: "https://github.com/Ada/Project",
      html_url: "https://github.com/org/repo/issues/1",
    },
  ]);

  assert.match(
    csv,
    /^Builder,Cohort,Milestone,Status,Late,Submitted,Updated,Repo,Issue\r\n/,
  );
  assert.match(csv, /"Ada, ""Data""",2026-A,M2,passed,no,/);
});

test("readDashboardState keeps valid filters and rejects invalid values", () => {
  assert.deepEqual(
    readDashboardState("?view=all&q=Ada&milestone=M2&status=passed"),
    {
      view: "all",
      q: "Ada",
      milestone: "M2",
      status: "passed",
    },
  );
  assert.deepEqual(
    readDashboardState("?view=hacked&milestone=M9&status=unknown"),
    {
      view: "enrolled",
      q: "",
      milestone: "",
      status: "",
    },
  );
});

test("buildDashboardQuery omits defaults and round-trips filters", () => {
  assert.equal(
    buildDashboardQuery({
      view: "enrolled",
      q: "",
      milestone: "",
      status: "",
    }),
    "",
  );
  const query = buildDashboardQuery({
    view: "non-enrolled",
    q: "Ada Lovelace",
    milestone: "M3",
    status: "ready-for-review",
  });
  assert.equal(
    query,
    "view=non-enrolled&q=Ada+Lovelace&milestone=M3&status=ready-for-review",
  );
  assert.deepEqual(readDashboardState(`?${query}`), {
    view: "non-enrolled",
    q: "Ada Lovelace",
    milestone: "M3",
    status: "ready-for-review",
  });
});
