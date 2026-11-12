const test = require("node:test");
const assert = require("node:assert/strict");

const {
  METADATA_LABELS,
  MILESTONES,
  STATE_LABELS,
  decideState,
  extractField,
  extractRepoUrl,
  extractRecheckHash,
  isAuthorizedCommenter,
  isLate,
  isOnTime,
  nextMilestone,
  parseTimestamp,
  previousMilestone,
} = require("./milestone_logic.js");

test("extractField reads GitHub issue-form headings", () => {
  const body =
    "### Builder Name\n\nAda\n\n### GitHub Repo URL\n\nhttps://github.com/Ada/Project.git\n";
  assert.equal(extractField(body, "Builder Name"), "Ada");
  assert.equal(
    extractField(body, "GitHub Repo URL"),
    "https://github.com/Ada/Project.git",
  );
  assert.equal(extractField(body, "Commit Hash"), "");
});

test("extractRepoUrl canonicalizes GitHub repository URLs", () => {
  assert.equal(
    extractRepoUrl("https://github.com/Ada/Project"),
    "https://github.com/Ada/Project",
  );
  assert.equal(
    extractRepoUrl("https://github.com/Ada/Project.git"),
    "https://github.com/Ada/Project",
  );
  assert.equal(
    extractRepoUrl("https://github.com/Ada/Project/blob/main/README.md"),
    "https://github.com/Ada/Project",
  );
  assert.equal(extractRepoUrl("https://gitlab.com/Ada/Project"), "");
  assert.equal(extractRepoUrl("not a url"), "");
});

test("deadline boundaries honor timezone offsets", () => {
  const deadline = "2026-07-12T23:59:59+08:00";
  assert.equal(isOnTime("2026-07-12T15:59:59Z", deadline), true);
  assert.equal(isOnTime("2026-07-12T16:00:00Z", deadline), false);
  assert.equal(isLate("2026-07-12T15:59:59Z", deadline), false);
  assert.equal(isLate("2026-07-12T16:00:00Z", deadline), true);
  assert.equal(
    new Date(parseTimestamp(deadline)).toISOString(),
    "2026-07-12T15:59:59.000Z",
  );
  assert.equal(isLate("2026-08-01T00:00:00Z", undefined), false);
});

test("late-submission is metadata, not a terminal state", () => {
  assert.ok(METADATA_LABELS.includes("late-submission"));
  assert.ok(!STATE_LABELS.includes("late-submission"));
});

test("milestone neighbors are sequential", () => {
  assert.equal(previousMilestone("M0"), null);
  assert.equal(nextMilestone("M6"), null);
  MILESTONES.slice(1).forEach((milestone, index) => {
    assert.equal(previousMilestone(milestone), MILESTONES[index]);
  });
  MILESTONES.slice(0, -1).forEach((milestone, index) => {
    assert.equal(nextMilestone(milestone), MILESTONES[index + 1]);
  });
  assert.equal(previousMilestone("unknown"), null);
  assert.equal(nextMilestone("unknown"), null);
});

test("extractRecheckHash accepts command and legacy forms", () => {
  assert.equal(
    extractRecheckHash("/recheck 0123456789abcdef0123456789abcdef01234567"),
    "0123456789abcdef0123456789abcdef01234567",
  );
  assert.equal(
    extractRecheckHash("Please /recheck ABCDEF0123456789ABCDEF0123456789ABCDEF01 now"),
    "abcdef0123456789abcdef0123456789abcdef01",
  );
  assert.equal(
    extractRecheckHash("0123456789abcdef0123456789abcdef01234567"),
    "0123456789abcdef0123456789abcdef01234567",
  );
  assert.equal(
    extractRecheckHash("commit 0123456789abcdef0123456789abcdef01234567"),
    "",
  );
  // GitHub renders commit links as 7-character short hashes by default.
  assert.equal(extractRecheckHash("/recheck a1b2c3d"), "a1b2c3d");
  assert.equal(extractRecheckHash("/recheck A1B2C3D"), "a1b2c3d");
  assert.equal(extractRecheckHash("a1b2c3d"), "a1b2c3d");
  assert.equal(extractRecheckHash("commit a1b2c3d"), "");
  // Shorter than a short hash must not be accepted.
  assert.equal(extractRecheckHash("/recheck a1b2c3"), "");
  assert.equal(extractRecheckHash("a1b2c3"), "");
});

test("isAuthorizedCommenter allows the author and maintainers", () => {
  assert.equal(isAuthorizedCommenter("Ada", "ada", "NONE"), true);
  assert.equal(isAuthorizedCommenter("Ada", "Grace", "OWNER"), true);
  assert.equal(isAuthorizedCommenter("Ada", "Grace", "MEMBER"), true);
  assert.equal(isAuthorizedCommenter("Ada", "Grace", "COLLABORATOR"), true);
  assert.equal(isAuthorizedCommenter("Ada", "Grace", "CONTRIBUTOR"), false);
  assert.equal(isAuthorizedCommenter("Ada", "Grace", "NONE"), false);
});

test("decideState maps check outcomes to labels", () => {
  assert.equal(
    decideState({ snapshotOk: false, prerequisiteOk: true }),
    "needs-improvement",
  );
  assert.equal(
    decideState({ snapshotOk: true, prerequisiteOk: false }),
    "waiting-on-prerequisite",
  );
  assert.equal(
    decideState({ snapshotOk: true, prerequisiteOk: true }),
    "ready-for-review",
  );
});
