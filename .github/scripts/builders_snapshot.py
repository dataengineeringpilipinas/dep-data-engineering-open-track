#!/usr/bin/env python3
"""Derive the public builder directory from the milestone issue snapshot.

The homepage used to render ``docs/data/builders.json``, a hand-exported roster
that drifted from the submission system. This module builds the same payload
from the issues fetched by ``progress-snapshot.yml`` plus
``.github/enrolled-participants.json`` so the directory follows both labels and
the allowlist automatically.

Prints ``changed`` or ``unchanged`` on success so the workflow can decide
whether to publish.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

MILESTONES = ["M0", "M1", "M2", "M3", "M4", "M5", "M6"]
PROCESS_LABELS = {
    "auto-check-pending",
    "waiting-on-prerequisite",
    "ready-for-review",
    "needs-improvement",
    "passed",
}
PUBLIC_STATUSES = {"Active", "Dropped", "Completed"}
PHILIPPINE_TZ = timezone(timedelta(hours=8))
COHORT_WEEKS = 24
DEFAULT_START_DATE = date(2026, 6, 22)
SOURCE = "GitHub milestone-submission issues + enrolled-participants.json"
M5_PHASE_PENDING = "Predictive / Alt Track"
M5_PHASE_A = "Predictive"
M5_PHASE_B = "Non-Predictive"
PHASE_BY_MILESTONE = {
    0: "Foundations",
    1: "Foundations",
    2: "Data Collection",
    3: "Data Processing",
    4: "Analysis & Insights",
}
TITLE_PATTERNS = (
    re.compile(r"^\[M[0-6]\]\s*(?P<builder>.*?)\s*[—–]\s*(?P<title>.+)$", re.I),
    re.compile(r"^\[M[0-6]\]\s*(?P<builder>.*?)\s+-\s+(?P<title>.+)$", re.I),
)


def label_names(issue: dict[str, Any]) -> list[str]:
    label_payload = issue.get("labels") or []
    names: list[str] = []
    for label in label_payload:
        if isinstance(label, dict):
            names.append(str(label.get("name") or ""))
        else:
            names.append(str(label))
    return names


def issue_milestone(issue: dict[str, Any]) -> str | None:
    for name in label_names(issue):
        milestone = name.strip().upper()
        if milestone in MILESTONES:
            return milestone
    return None


def issue_status(issue: dict[str, Any]) -> str:
    names = set(label_names(issue))
    if "passed" in names:
        return "passed"
    for status in (
        "needs-improvement",
        "waiting-on-prerequisite",
        "ready-for-review",
        "auto-check-pending",
    ):
        if status in names:
            return status
    return "pending-review"


def is_countable(issue: dict[str, Any]) -> bool:
    """Match the tracker's filters: no PRs, duplicates, or late-only legacy issues."""
    if issue.get("pull_request"):
        return False
    names = set(label_names(issue))
    if "duplicate" in names:
        return False
    if "late-submission" in names and not (names & PROCESS_LABELS):
        return False
    return True


def extract_field(body: str | None, heading: str) -> str:
    match = re.search(
        rf"###\s+{re.escape(heading)}\s*\n+([^\n#]+)",
        body or "",
        re.IGNORECASE,
    )
    return match.group(1).strip() if match else ""


def project_title(issue: dict[str, Any] | None) -> str:
    if not issue:
        return ""
    title = str(issue.get("title") or "").strip()
    for pattern in TITLE_PATTERNS:
        match = pattern.match(title)
        if match:
            value = match.group("title").strip()
            return value.strip("<>").strip().strip("\"'").strip()
    return ""


def latest_issue(issues: list[dict[str, Any]]) -> dict[str, Any] | None:
    return max(
        issues,
        key=lambda issue: (
            str(issue.get("created_at") or ""),
            int(issue.get("number") or 0),
        ),
        default=None,
    )


def latest_project_title(issues: list[dict[str, Any]]) -> str:
    for issue in sorted(
        issues,
        key=lambda item: (
            str(item.get("created_at") or ""),
            int(item.get("number") or 0),
        ),
        reverse=True,
    ):
        title = project_title(issue)
        if title:
            return title
    return ""


def m5_phase(issues: list[dict[str, Any]]) -> str:
    latest = latest_issue(issues)
    if not latest:
        return M5_PHASE_PENDING
    path = extract_field(latest.get("body"), "Which path did you take?").lower()
    if path.startswith("path a"):
        return M5_PHASE_A
    if path.startswith("path b"):
        return M5_PHASE_B
    return M5_PHASE_PENDING


def phase_for(milestone: int, m5_issues: list[dict[str, Any]]) -> str:
    if milestone == 5:
        return m5_phase(m5_issues)
    if milestone == 6:
        return "Packaging & Deployment"
    return PHASE_BY_MILESTONE.get(milestone, "Foundations")


def active_week(generated_at: datetime, start_date: date) -> int:
    if generated_at.tzinfo is None:
        generated_at = generated_at.replace(tzinfo=timezone.utc)
    local_date = generated_at.astimezone(PHILIPPINE_TZ).date()
    week = max(1, (local_date - start_date).days // 7 + 1)
    return min(week, COHORT_WEEKS)


def build_builders_snapshot(
    issues: list[dict[str, Any]],
    allowlist: dict[str, Any],
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or datetime.now(timezone.utc)
    if generated_at.tzinfo is None:
        generated_at = generated_at.replace(tzinfo=timezone.utc)
    start_date = parse_start_date(allowlist.get("start_date"))
    participants = [str(user) for user in allowlist.get("participants") or []]
    display_names = casefold_map(allowlist.get("display_names") or {})
    name_opt_outs = {str(user).lower() for user in allowlist.get("name_opt_outs") or []}
    status_overrides = casefold_map(allowlist.get("status_overrides") or {})

    by_login: dict[str, list[dict[str, Any]]] = {}
    for issue in issues:
        if not is_countable(issue):
            continue
        login = str((issue.get("user") or {}).get("login") or "").lower()
        if login:
            by_login.setdefault(login, []).append(issue)

    builders: list[dict[str, Any]] = []
    for login in participants:
        key = login.lower()
        builder_issues = by_login.get(key, [])
        submissions = [
            issue for issue in builder_issues if issue_milestone(issue) is not None
        ]
        submitted_milestones = {
            issue_milestone(issue) for issue in submissions if issue_milestone(issue)
        }
        passed_milestones = [
            MILESTONES.index(issue_milestone(issue))
            for issue in submissions
            if issue_status(issue) == "passed" and issue_milestone(issue)
        ]
        highest_passed = max(passed_milestones, default=-1)
        current_milestone = max(0, min(highest_passed + 1, 6))
        latest = latest_issue(submissions)

        name = display_names.get(key) or ""
        if key in name_opt_outs:
            name = login
        elif not name:
            name = extract_field(latest.get("body"), "Builder Name") if latest else ""
            name = name or login

        status = status_overrides.get(key, "")
        if status:
            if status not in PUBLIC_STATUSES:
                raise ValueError(
                    f"Unsupported public status override for {login}: {status!r}"
                )
        else:
            status = "Completed" if highest_passed >= 6 else "Active"

        builders.append(
            {
                "name": name,
                "github": f"https://github.com/{login}",
                "status": status,
                "projectTopic": latest_project_title(submissions),
                "startDate": start_date.isoformat(),
                "activeWeek": f"W{active_week(generated_at, start_date)}",
                "currentMilestone": current_milestone,
                "milestonesSubmitted": len(submitted_milestones),
                "milestonesPassed": highest_passed + 1,
                "phase": phase_for(
                    current_milestone,
                    [
                        issue
                        for issue in submissions
                        if issue_milestone(issue) == "M5"
                    ],
                ),
            }
        )

    return {
        "cohort": allowlist.get("cohort") or "2026 Open Track",
        "updatedAt": generated_at.astimezone(PHILIPPINE_TZ).date().isoformat(),
        "source": SOURCE,
        "builders": builders,
    }


def builders_changed(
    existing: dict[str, Any] | None,
    snapshot: dict[str, Any],
) -> bool:
    """Compare everything except the publish timestamp."""
    if not isinstance(existing, dict):
        return True
    if not isinstance(existing.get("builders"), list):
        return True
    return without_timestamp(existing) != without_timestamp(snapshot)


def without_timestamp(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in snapshot.items() if key != "updatedAt"}


def casefold_map(value: dict[str, Any]) -> dict[str, str]:
    return {str(key).lower(): str(item) for key, item in value.items()}


def parse_start_date(value: Any) -> date:
    if not value:
        return DEFAULT_START_DATE
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value))


def load_json(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def write_snapshot(path: str | Path, snapshot: dict[str, Any]) -> None:
    Path(path).write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issues", required=True, help="Fresh issue list from gh api")
    parser.add_argument(
        "--allowlist",
        required=True,
        help="Enrollment allowlist with participants and display metadata",
    )
    parser.add_argument(
        "--existing",
        help="Builder snapshot currently on the data branch (optional)",
    )
    parser.add_argument("--output", required=True, help="Where to write a changed snapshot")
    parser.add_argument(
        "--now",
        help="ISO-8601 timestamp used for the active week and updatedAt",
    )
    args = parser.parse_args(argv)

    try:
        issues = load_json(args.issues)
        allowlist = load_json(args.allowlist)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not read input: {error}", file=sys.stderr)
        return 2

    if not isinstance(issues, list):
        print("Issue payload must be a JSON array.", file=sys.stderr)
        return 2
    if not isinstance(allowlist, dict):
        print("Allowlist payload must be a JSON object.", file=sys.stderr)
        return 2

    existing = None
    if args.existing and Path(args.existing).exists():
        try:
            existing = load_json(args.existing)
        except (OSError, json.JSONDecodeError):
            # A malformed snapshot should be replaced, not block publishing.
            existing = None

    try:
        snapshot = build_builders_snapshot(
            issues,
            allowlist,
            generated_at=parse_timestamp(args.now),
        )
    except (TypeError, ValueError) as error:
        print(f"Could not build builder snapshot: {error}", file=sys.stderr)
        return 2

    if not builders_changed(existing, snapshot):
        print("unchanged")
        return 0

    write_snapshot(args.output, snapshot)
    print("changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
