#!/usr/bin/env python3
"""Build and compare the JSON payload published by progress-snapshot.yml.

The workflow calls this after fetching issues. Keeping the comparison here,
rather than in inline jq, means the "only publish when the data changed" rule
is covered by the same pytest suite as the milestone scripts.

Prints ``changed`` or ``unchanged`` on success so the workflow can decide
whether to publish.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return issues in a stable order so API ordering does not cause churn."""
    return sorted(issues, key=lambda issue: int(issue.get("number", 0)))


def build_snapshot(
    issues: list[dict[str, Any]],
    generated_at: str | None = None,
) -> dict[str, Any]:
    return {
        "generated_at": generated_at
        or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "issues": canonical_issues(issues),
    }


def snapshot_changed(
    existing: dict[str, Any] | None,
    issues: list[dict[str, Any]],
) -> bool:
    """Compare only the issue data; generated_at changes on every run."""
    if not isinstance(existing, dict):
        return True
    existing_issues = existing.get("issues")
    if not isinstance(existing_issues, list):
        return True
    return canonical_issues(existing_issues) != canonical_issues(issues)


def load_json(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def write_snapshot(path: str | Path, snapshot: dict[str, Any]) -> None:
    Path(path).write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issues", required=True, help="Fresh issue list from gh api")
    parser.add_argument(
        "--existing",
        help="Snapshot currently on the data branch (optional)",
    )
    parser.add_argument("--output", required=True, help="Where to write a changed snapshot")
    args = parser.parse_args(argv)

    try:
        issues = load_json(args.issues)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not read issues: {error}", file=sys.stderr)
        return 2

    if not isinstance(issues, list):
        print("Issue payload must be a JSON array.", file=sys.stderr)
        return 2

    existing = None
    if args.existing and Path(args.existing).exists():
        try:
            existing = load_json(args.existing)
        except (OSError, json.JSONDecodeError):
            # A malformed or missing snapshot should be replaced, not block publishing.
            existing = None

    if not snapshot_changed(existing, issues):
        print("unchanged")
        return 0

    write_snapshot(args.output, build_snapshot(issues))
    print("changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
