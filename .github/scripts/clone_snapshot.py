"""
Clone a builder repository and check out the submitted commit.

Short commit hashes resolve only when the commit is reachable from an
advertised ref. GitHub resolves unadvertised commits only by full 40-character
hash, so an orphaned or force-pushed commit submitted as a short hash fails
with a distinct, actionable error.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

SHA_PATTERN = re.compile(r"^[0-9a-fA-F]{7,40}$")

INVALID_ERROR = "The repository URL or commit hash is invalid."
CLONE_ERROR = "The repository could not be cloned. Confirm it is public."
SHORT_SHA_ERROR = (
    "The short commit hash could not be resolved. If this commit is no longer "
    "on a branch (for example after a force-push or rebase), comment "
    "`/recheck <full 40-character hash>` on this issue."
)
NOT_FOUND_ERROR = "The submitted commit was not found in the repository."


def run_git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def resolve_commit(dest: Path, commit_hash: str) -> str | None:
    """Return the full SHA for commit_hash, or None if it cannot be resolved."""
    local = run_git("rev-parse", "--verify", "--quiet", f"{commit_hash}^{{commit}}", cwd=dest)
    if local.returncode == 0:
        return local.stdout.strip()

    # The commit is not reachable from a fetched ref. GitHub serves unadvertised
    # objects when asked for the full SHA, but cannot expand a short hash.
    fetched = run_git("fetch", "--depth", "1", "origin", commit_hash, cwd=dest)
    if fetched.returncode != 0:
        return None

    resolved = run_git("rev-parse", "--verify", "--quiet", f"{commit_hash}^{{commit}}", cwd=dest)
    if resolved.returncode != 0:
        return None
    return resolved.stdout.strip()


def clone_snapshot(repo_url: str, commit_hash: str, dest: Path) -> tuple[bool, str]:
    """Clone repo_url into dest and check out commit_hash.

    Returns (True, "") on success or (False, error_message) on failure.
    """
    if not repo_url or not SHA_PATTERN.match(commit_hash or ""):
        return False, INVALID_ERROR

    clone = run_git("clone", "--filter=blob:none", "--no-checkout", repo_url, str(dest))
    if clone.returncode != 0:
        print(clone.stderr.strip(), file=sys.stderr)
        return False, CLONE_ERROR

    resolved = resolve_commit(dest, commit_hash)
    if resolved is None:
        error = SHORT_SHA_ERROR if len(commit_hash) < 40 else NOT_FOUND_ERROR
        return False, error

    checkout = run_git("checkout", "--detach", resolved, cwd=dest)
    if checkout.returncode != 0:
        print(checkout.stderr.strip(), file=sys.stderr)
        return False, NOT_FOUND_ERROR

    return True, ""


def write_output(path: str, clone_ok: bool, error: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"clone_ok={'true' if clone_ok else 'false'}\n")
        if error:
            f.write(f"clone_error={error}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-url", required=True)
    parser.add_argument("--commit-hash", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))
    args = parser.parse_args(argv)

    clone_ok, error = clone_snapshot(args.repo_url, args.commit_hash, Path(args.dest))

    if args.github_output:
        write_output(args.github_output, clone_ok, error)
    else:
        print(f"clone_ok={'true' if clone_ok else 'false'}")
        if error:
            print(f"clone_error={error}")

    # The workflow reads the result from GITHUB_OUTPUT, so this command should
    # not fail the step just because the clone itself did not succeed.
    return 0


if __name__ == "__main__":
    sys.exit(main())
