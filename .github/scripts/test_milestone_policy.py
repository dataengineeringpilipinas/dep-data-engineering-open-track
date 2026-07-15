from datetime import timezone

import pytest

from milestone_policy import (
    MILESTONES,
    choose_latest_on_time,
    decide_state,
    extract_field,
    extract_recheck_hash,
    is_on_time,
    next_milestone,
    normalize_repo_url,
    parse_timestamp,
    previous_milestone,
)


def test_extract_field_from_issue_form_body():
    body = "### Builder Name\n\nAda\n\n### GitHub Repo URL\n\nhttps://github.com/Ada/Project.git\n"
    assert extract_field(body, "Builder Name") == "Ada"
    assert extract_field(body, "GitHub Repo URL") == "https://github.com/Ada/Project.git"
    assert extract_field(body, "Commit Hash") == ""


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://github.com/Ada/Project", "ada/project"),
        ("https://github.com/Ada/Project.git", "ada/project"),
        ("https://github.com/Ada/Project/blob/main/README.md", "ada/project"),
        ("https://gitlab.com/Ada/Project", ""),
        ("not a url", ""),
    ],
)
def test_normalize_repo_url(url, expected):
    assert normalize_repo_url(url) == expected


def test_deadline_boundary_uses_timezone_offset():
    deadline = "2026-07-12T23:59:59+08:00"
    assert is_on_time("2026-07-12T15:59:59Z", deadline)
    assert not is_on_time("2026-07-12T16:00:00Z", deadline)
    assert parse_timestamp(deadline).astimezone(timezone.utc).isoformat() == "2026-07-12T15:59:59+00:00"


def test_all_milestone_neighbors_are_sequential():
    assert previous_milestone("M0") is None
    assert next_milestone("M6") is None
    for index, milestone in enumerate(MILESTONES[1:], start=1):
        assert previous_milestone(milestone) == MILESTONES[index - 1]
    for index, milestone in enumerate(MILESTONES[:-1]):
        assert next_milestone(milestone) == MILESTONES[index + 1]


@pytest.mark.parametrize(
    ("comment", "expected"),
    [
        ("/recheck 0123456789abcdef0123456789abcdef01234567", "0123456789abcdef0123456789abcdef01234567"),
        ("Please /recheck ABCDEF0123456789ABCDEF0123456789ABCDEF01 now", "abcdef0123456789abcdef0123456789abcdef01"),
        ("0123456789abcdef0123456789abcdef01234567", "0123456789abcdef0123456789abcdef01234567"),
        ("commit 0123456789abcdef0123456789abcdef01234567", ""),
    ],
)
def test_extract_recheck_hash(comment, expected):
    assert extract_recheck_hash(comment) == expected


@pytest.mark.parametrize(
    ("deadline_ok", "snapshot_ok", "prerequisite_ok", "expected"),
    [
        (False, True, True, "late-submission"),
        (True, False, True, "needs-improvement"),
        (True, True, False, "waiting-on-prerequisite"),
        (True, True, True, "ready-for-review"),
    ],
)
def test_decide_state(deadline_ok, snapshot_ok, prerequisite_ok, expected):
    assert decide_state(
        deadline_ok=deadline_ok,
        snapshot_ok=snapshot_ok,
        prerequisite_ok=prerequisite_ok,
    ) == expected


def test_choose_latest_on_time_ignores_late_replacement():
    deadline = "2026-07-12T23:59:59+08:00"
    issues = [
        {"number": 1, "created_at": "2026-07-12T12:00:00Z"},
        {"number": 2, "created_at": "2026-07-12T15:00:00Z"},
        {"number": 3, "created_at": "2026-07-12T16:00:00Z"},
    ]
    assert choose_latest_on_time(issues, deadline)["number"] == 2
