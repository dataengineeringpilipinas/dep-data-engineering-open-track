"""Pure policy helpers for milestone tooling and regression tests.

GitHub API mutations stay in the workflows. Keeping parsing and state decisions
here makes deadline classification, identity, and milestone rules independently testable.
"""

from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urlparse


MILESTONES = ("M0", "M1", "M2", "M3", "M4", "M5", "M6")
STATE_LABELS = (
    "auto-check-pending",
    "waiting-on-prerequisite",
    "ready-for-review",
    "needs-improvement",
    "passed",
)
METADATA_LABELS = ("late-submission",)


def extract_field(body: str, heading: str) -> str:
    """Extract a value from GitHub issue-form ``### Heading`` output.

    Regex pattern must stay in sync with the JS ``extract`` helper in
    .github/workflows/_milestone-evaluate.yml and notify-reviewer.yml.
    """
    match = re.search(
        rf"###\s+{re.escape(heading)}\s*\n+([^\n#]+)",
        body or "",
        flags=re.IGNORECASE,
    )
    return match.group(1).strip() if match else ""


def normalize_repo_url(value: str) -> str:
    """Return a lowercase ``owner/repo`` identity for a GitHub repository URL."""
    raw = (value or "").strip()
    try:
        parsed = urlparse(raw)
    except ValueError:
        return ""

    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "github.com":
        return ""

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return ""

    owner = parts[0]
    repo = parts[1]
    if repo.lower().endswith(".git"):
        repo = repo[:-4]
    if not owner or not repo:
        return ""
    return f"{owner}/{repo}".lower()


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO-8601 timestamp, including a trailing ``Z``."""
    normalized = (value or "").strip().replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def is_on_time(created_at: str, deadline: str) -> bool:
    return parse_timestamp(created_at) <= parse_timestamp(deadline)


def is_late(created_at: str, deadline: str) -> bool:
    """Return whether a submission should receive informational late metadata."""
    return parse_timestamp(created_at) > parse_timestamp(deadline)


def previous_milestone(milestone: str) -> str | None:
    try:
        index = MILESTONES.index(milestone.upper())
    except ValueError:
        return None
    return MILESTONES[index - 1] if index > 0 else None


def next_milestone(milestone: str) -> str | None:
    try:
        index = MILESTONES.index(milestone.upper())
    except ValueError:
        return None
    return MILESTONES[index + 1] if index < len(MILESTONES) - 1 else None


def extract_recheck_hash(comment: str) -> str:
    """Accept ``/recheck <hash>`` and legacy comments containing only a hash."""
    text = (comment or "").strip()
    command = re.search(r"(?:^|\s)/recheck\s+([0-9a-f]{40})(?:\s|$)", text, re.I)
    if command:
        return command.group(1).lower()
    if re.fullmatch(r"[0-9a-f]{40}", text, re.I):
        return text.lower()
    return ""


def decide_state(*, snapshot_ok: bool, prerequisite_ok: bool) -> str:
    """Return the single workflow state that should follow evaluation."""
    if not snapshot_ok:
        return "needs-improvement"
    if not prerequisite_ok:
        return "waiting-on-prerequisite"
    return "ready-for-review"


def choose_latest_on_time(issues: list[dict], deadline: str) -> dict | None:
    """Choose the newest issue that still preserves deadline eligibility."""
    eligible = [issue for issue in issues if is_on_time(issue["created_at"], deadline)]
    if not eligible:
        return None
    return max(eligible, key=lambda issue: (parse_timestamp(issue["created_at"]), issue["number"]))
