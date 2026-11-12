// Shared helpers for the progress dashboard. Kept in a small standalone file
// so the snapshot, URL-state, escaping, and CSV rules can be unit-tested
// outside the browser.
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    root.ProgressSnapshot = api;
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const DEFAULT_OWNER = "dataengineeringpilipinas";
  const DEFAULT_REPO = "dep-data-engineering-open-track";
  const DEFAULT_BRANCH = "progress-data";
  const DEFAULT_VIEW = "enrolled";
  const STALE_HOURS = 12;
  const VIEWS = ["enrolled", "non-enrolled", "all"];
  const STATUSES = [
    "pending-review",
    "ready-for-review",
    "waiting-on-prerequisite",
    "needs-improvement",
    "passed",
    "checking",
  ];
  const HTML_ESCAPES = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  };

  function snapshotUrl(
    owner = DEFAULT_OWNER,
    repo = DEFAULT_REPO,
    branch = DEFAULT_BRANCH,
  ) {
    return `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/progress-snapshot.json`;
  }

  function parseGeneratedAt(value) {
    if (!value) return null;
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function formatSnapshotStatus(generatedAt, now = Date.now()) {
    const date = parseGeneratedAt(generatedAt);
    if (!date) {
      return { text: "Snapshot timestamp unavailable", stale: true };
    }

    const stamp = date.toLocaleString("en-PH", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "Asia/Manila",
    });
    const ageHours = Math.floor(Math.max(0, now - date.getTime()) / 3600000);

    if (ageHours >= STALE_HOURS) {
      return {
        text: `Snapshot from ${stamp} (${ageHours}h old — refresh may be delayed)`,
        stale: true,
      };
    }
    return { text: `Snapshot from ${stamp}`, stale: false };
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(
      /[&<>"']/g,
      (character) => HTML_ESCAPES[character],
    );
  }

  function safeExternalUrl(value) {
    if (!value || value === "—") return "";
    try {
      const url = new URL(value);
      return url.protocol === "http:" || url.protocol === "https:"
        ? url.href
        : "";
    } catch (_) {
      return "";
    }
  }

  function csvCell(value) {
    const raw = value == null ? "" : String(value);
    // Prevent spreadsheet formula execution from issue-controlled fields.
    const text = /^[=+\-@\t\r]/.test(raw) ? `'${raw}` : raw;
    return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
  }

  function buildCsv(issues) {
    const columns = [
      ["Builder", (issue) => issue._builder],
      ["Cohort", (issue) => issue._cohort],
      ["Milestone", (issue) => issue._milestone],
      ["Status", (issue) => issue._status],
      ["Late", (issue) => (issue._isLate ? "yes" : "no")],
      ["Submitted", (issue) => issue.created_at],
      ["Updated", (issue) => issue.updated_at],
      ["Repo", (issue) => issue._repoUrl],
      ["Issue", (issue) => issue.html_url],
    ];
    const rows = [
      columns.map(([label]) => csvCell(label)).join(","),
      ...issues.map((issue) =>
        columns.map(([, value]) => csvCell(value(issue))).join(","),
      ),
    ];
    return rows.join("\r\n");
  }

  function readDashboardState(search = "") {
    const params = new URLSearchParams(search);
    const view = params.get("view");
    const milestone = params.get("milestone");
    const status = params.get("status");
    return {
      view: VIEWS.includes(view) ? view : DEFAULT_VIEW,
      q: (params.get("q") || "").slice(0, 200),
      milestone: /^M[0-6]$/.test(milestone || "") ? milestone : "",
      status: STATUSES.includes(status) ? status : "",
    };
  }

  function buildDashboardQuery(state) {
    const params = new URLSearchParams();
    if (state.view && state.view !== DEFAULT_VIEW)
      params.set("view", state.view);
    if (state.q) params.set("q", state.q);
    if (state.milestone) params.set("milestone", state.milestone);
    if (state.status) params.set("status", state.status);
    return params.toString();
  }

  return {
    snapshotUrl,
    parseGeneratedAt,
    formatSnapshotStatus,
    escapeHtml,
    safeExternalUrl,
    csvCell,
    buildCsv,
    readDashboardState,
    buildDashboardQuery,
    DEFAULT_VIEW,
    STALE_HOURS,
    VIEWS,
    STATUSES,
  };
});
