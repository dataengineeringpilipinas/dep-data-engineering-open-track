// Shared helpers for the progress snapshot. Kept in a small standalone file so
// the URL and staleness rules can be unit-tested outside the browser.
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
  const STALE_HOURS = 12;

  function snapshotUrl(owner = DEFAULT_OWNER, repo = DEFAULT_REPO, branch = DEFAULT_BRANCH) {
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

  return {
    snapshotUrl,
    parseGeneratedAt,
    formatSnapshotStatus,
    STALE_HOURS,
  };
});
