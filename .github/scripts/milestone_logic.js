"use strict";

/**
 * Shared milestone policy helpers.
 *
 * This is the single source of truth for field extraction, repo/commit
 * parsing, deadline classification, milestone sequencing, and state decisions.
 * The workflows require it directly (via actions/github-script) and the Node
 * test suite exercises the same file, so runtime and tested logic cannot drift.
 */

const MILESTONES = ["M0", "M1", "M2", "M3", "M4", "M5", "M6"];

const STATE_LABELS = [
  "auto-check-pending",
  "waiting-on-prerequisite",
  "ready-for-review",
  "needs-improvement",
  "passed",
];

const METADATA_LABELS = ["late-submission"];

const AUTHORIZED_ASSOCIATIONS = ["OWNER", "MEMBER", "COLLABORATOR"];

/** Extract a value from GitHub issue-form ``### Heading`` output. */
function extractField(body, heading) {
  const match = (body || "").match(
    new RegExp(`###\\s+${heading}\\s*\\n+([^\\n#]+)`, "i"),
  );
  return match ? match[1].trim() : "";
}

/**
 * Return a canonical ``https://github.com/owner/repo`` URL, or ``""`` when the
 * value is not a GitHub repository URL. Used to keep ``git clone`` constrained
 * to github.com.
 */
function extractRepoUrl(value) {
  const match = (value || "")
    .trim()
    .match(/^https?:\/\/github\.com\/([\w.-]+)\/([\w.-]+?)(?:\.git)?(?:\/|$)/i);
  return match ? `https://github.com/${match[1]}/${match[2]}` : "";
}

/** Parse an ISO-8601 timestamp to epoch milliseconds (NaN when invalid). */
function parseTimestamp(value) {
  return new Date(value).getTime();
}

function isOnTime(createdAt, deadline) {
  return parseTimestamp(createdAt) <= parseTimestamp(deadline);
}

/** Return whether a submission should receive informational late metadata. */
function isLate(createdAt, deadline) {
  return Boolean(deadline) && parseTimestamp(createdAt) > parseTimestamp(deadline);
}

function previousMilestone(milestone) {
  const index = MILESTONES.indexOf(String(milestone || "").toUpperCase());
  return index > 0 ? MILESTONES[index - 1] : null;
}

function nextMilestone(milestone) {
  const index = MILESTONES.indexOf(String(milestone || "").toUpperCase());
  return index >= 0 && index < MILESTONES.length - 1
    ? MILESTONES[index + 1]
    : null;
}

/**
 * Accept ``/recheck <hash>`` and legacy comments containing only a hash.
 * Returns a lowercase hash, or ``""`` when none is present.
 */
function extractRecheckHash(comment) {
  const text = (comment || "").trim();
  const command = text.match(/(?:^|\s)\/recheck\s+([0-9a-f]{7,40})(?:\s|$)/i);
  if (command) return command[1].toLowerCase();
  const legacy = text.match(/^[0-9a-f]{7,40}$/i);
  return legacy ? legacy[0].toLowerCase() : "";
}

/** True if the commenter is the issue author or a maintainer. */
function isAuthorizedCommenter(issueAuthor, commentAuthor, authorAssociation) {
  return (
    String(commentAuthor || "").toLowerCase() ===
      String(issueAuthor || "").toLowerCase() ||
    AUTHORIZED_ASSOCIATIONS.includes(authorAssociation)
  );
}

/** Return the single workflow state label that should follow evaluation. */
function decideState({ snapshotOk, prerequisiteOk }) {
  if (!snapshotOk) return "needs-improvement";
  if (!prerequisiteOk) return "waiting-on-prerequisite";
  return "ready-for-review";
}

module.exports = {
  MILESTONES,
  STATE_LABELS,
  METADATA_LABELS,
  AUTHORIZED_ASSOCIATIONS,
  extractField,
  extractRepoUrl,
  parseTimestamp,
  isOnTime,
  isLate,
  previousMilestone,
  nextMilestone,
  extractRecheckHash,
  isAuthorizedCommenter,
  decideState,
};
