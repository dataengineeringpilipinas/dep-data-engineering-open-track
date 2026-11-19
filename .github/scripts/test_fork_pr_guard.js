"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");

const {
  assessPullRequest,
  isProtectedPath,
} = require("./fork_pr_guard.js");

const BASE = "dataengineeringpilipinas/dep-data-engineering-open-track";
const FORK = "builder/dep-data-engineering-open-track";

function file(filename, status = "removed") {
  return { filename, status };
}

test("protected paths cover automation, curriculum, cohorts, and docs", () => {
  for (const path of [
    ".github/workflows/ci.yml",
    "01-foundations/week-01/README.md",
    "02-data-collection/README.md",
    "cohorts/starter-kit/README.md",
    "docs/index.html",
  ]) {
    assert.equal(isProtectedPath(path), true, path);
  }
  for (const path of [
    "README.md",
    "data/raw/data.csv",
    "notebooks/analysis.ipynb",
    "reference-docs/local.md",
  ]) {
    assert.equal(isProtectedPath(path), false, path);
  }
});

test("same-repo PRs are never suspicious", () => {
  const result = assessPullRequest({
    headRepoFullName: BASE,
    baseRepoFullName: BASE,
    files: [file(".github/workflows/ci.yml")],
  });
  assert.equal(result.isFork, false);
  assert.equal(result.suspicious, false);
});

test("fork PRs deleting a protected file are suspicious", () => {
  const result = assessPullRequest({
    headRepoFullName: FORK,
    baseRepoFullName: BASE,
    files: [
      file(".github/workflows/ci.yml"),
      file("README.md", "modified"),
    ],
  });
  assert.equal(result.suspicious, true);
  assert.deepEqual(result.protectedDeletions, [".github/workflows/ci.yml"]);
  assert.match(result.reason, /protected file/);
});

test("fork PRs deleting more than 20 files are suspicious", () => {
  const files = Array.from({ length: 21 }, (_, index) =>
    file(`data/raw/file-${index}.csv`),
  );
  const result = assessPullRequest({
    headRepoFullName: FORK,
    baseRepoFullName: BASE,
    files,
  });
  assert.equal(result.suspicious, true);
  assert.equal(result.deletedCount, 21);
  assert.match(result.reason, /21 files/);
});

test("fork PRs deleting exactly 20 ordinary files are not suspicious", () => {
  const files = Array.from({ length: 20 }, (_, index) =>
    file(`data/raw/file-${index}.csv`),
  );
  const result = assessPullRequest({
    headRepoFullName: FORK,
    baseRepoFullName: BASE,
    files,
  });
  assert.equal(result.suspicious, false);
  assert.equal(result.deletedCount, 20);
});

test("fork PRs that only modify protected files are not suspicious", () => {
  const result = assessPullRequest({
    headRepoFullName: FORK,
    baseRepoFullName: BASE,
    files: [file("docs/index.html", "modified")],
  });
  assert.equal(result.suspicious, false);
});

test("a deleted head repo is treated as a fork", () => {
  const result = assessPullRequest({
    headRepoFullName: "",
    baseRepoFullName: BASE,
    files: [file("cohorts/starter-kit/README.md")],
  });
  assert.equal(result.isFork, true);
  assert.equal(result.suspicious, true);
});
