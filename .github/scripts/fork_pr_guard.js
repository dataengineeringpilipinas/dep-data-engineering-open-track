"use strict";

/**
 * Shared decision logic for the fork PR guard.
 *
 * The workflow runs on `pull_request_target` with a write token. This module
 * only receives PR metadata (repo names and changed-file statuses) so it never
 * reads or executes code from the fork.
 */

const DEFAULT_DELETED_FILE_THRESHOLD = 20;

const PROTECTED_PATH_PATTERNS = [
  /^\.github\//,
  /^docs\//,
  /^cohorts\//,
  /^\d{2}-[^/]+\//,
];

function isProtectedPath(filename) {
  return PROTECTED_PATH_PATTERNS.some((pattern) =>
    pattern.test(String(filename || "")),
  );
}

function assessPullRequest({
  headRepoFullName,
  baseRepoFullName,
  files,
  deletedFileThreshold = DEFAULT_DELETED_FILE_THRESHOLD,
}) {
  const isFork =
    String(headRepoFullName || "") !== String(baseRepoFullName || "");
  const removed = (files || []).filter((file) => file.status === "removed");
  const protectedDeletions = removed
    .filter((file) => isProtectedPath(file.filename))
    .map((file) => file.filename)
    .sort();

  const suspicious =
    isFork &&
    (protectedDeletions.length > 0 || removed.length > deletedFileThreshold);

  let reason = "not a fork";
  if (isFork && protectedDeletions.length > 0) {
    reason = `deletes ${protectedDeletions.length} protected file(s)`;
  } else if (isFork && removed.length > deletedFileThreshold) {
    reason = `deletes ${removed.length} files`;
  } else if (isFork) {
    reason = "no protected deletions";
  }

  return {
    isFork,
    suspicious,
    reason,
    deletedCount: removed.length,
    protectedDeletions,
  };
}

module.exports = {
  DEFAULT_DELETED_FILE_THRESHOLD,
  PROTECTED_PATH_PATTERNS,
  isProtectedPath,
  assessPullRequest,
};
