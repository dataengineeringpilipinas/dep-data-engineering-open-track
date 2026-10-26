from datetime import date, datetime, timezone

import pytest

from builders_snapshot import (
    active_week,
    build_builders_snapshot,
    builders_changed,
    project_title,
)

NOW = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)


def allowlist(**overrides):
    payload = {
        "cohort": "2026-A",
        "start_date": "2026-06-22",
        "participants": ["Ada", "Grace", "Linus"],
        "display_names": {
            "Ada": "Lovelace, Ada",
            "Grace": "Hopper, Grace",
        },
        "name_opt_outs": [],
        "status_overrides": {},
    }
    payload.update(overrides)
    return payload


def issue(
    number,
    login,
    milestone="M0",
    statuses=("passed",),
    body="",
    title=None,
    created_at="2026-06-25T00:00:00Z",
    pull_request=False,
    labels=None,
):
    if labels is not None:
        label_payload = [{"name": name} for name in labels]
    else:
        label_payload = [{"name": "milestone-submission"}]
        if milestone:
            label_payload.append({"name": milestone})
        label_payload.extend({"name": status} for status in statuses)
    return {
        "number": number,
        "title": title if title is not None else f"[{milestone}] {login} — Project {number}",
        "labels": label_payload,
        "user": {"login": login},
        "body": body,
        "created_at": created_at,
        "updated_at": created_at,
        "closed_at": None,
        "pull_request": pull_request,
    }


def builder_for(snapshot, login):
    return next(
        builder
        for builder in snapshot["builders"]
        if builder["github"].lower().endswith(f"/{login}".lower())
    )


def test_builder_list_comes_from_allowlist_even_without_issues():
    snapshot = build_builders_snapshot([], allowlist(), NOW)

    assert [builder["name"] for builder in snapshot["builders"]] == [
        "Lovelace, Ada",
        "Hopper, Grace",
        "Linus",
    ]
    linus = builder_for(snapshot, "Linus")
    assert linus["status"] == "Active"
    assert linus["currentMilestone"] == 0
    assert linus["milestonesSubmitted"] == 0
    assert linus["milestonesPassed"] == 0
    assert linus["phase"] == "Foundations"
    assert linus["activeWeek"] == "W19"
    assert linus["projectTopic"] == ""


def test_later_pass_implies_earlier_passes_and_current_milestone():
    snapshot = build_builders_snapshot(
        [issue(1, "Ada", "M0"), issue(2, "Ada", "M3")],
        allowlist(),
        NOW,
    )

    ada = builder_for(snapshot, "Ada")
    assert ada["milestonesSubmitted"] == 2
    assert ada["milestonesPassed"] == 4
    assert ada["currentMilestone"] == 4
    assert ada["phase"] == "Analysis & Insights"


def test_distinct_milestone_submissions_are_counted_once():
    snapshot = build_builders_snapshot(
        [
            issue(1, "Ada", "M1", statuses=("passed",)),
            issue(2, "Ada", "M1", statuses=("needs-improvement",)),
        ],
        allowlist(),
        NOW,
    )

    ada = builder_for(snapshot, "Ada")
    assert ada["milestonesSubmitted"] == 1
    assert ada["milestonesPassed"] == 2


def test_duplicate_late_only_and_pull_requests_are_excluded():
    snapshot = build_builders_snapshot(
        [
            issue(1, "Grace", "M2", labels=["milestone-submission", "M2", "passed"]),
            issue(2, "Grace", "M3", labels=["milestone-submission", "M3", "duplicate", "passed"]),
            issue(3, "Grace", "M4", labels=["milestone-submission", "M4", "late-submission"]),
            issue(
                4,
                "Grace",
                "M5",
                labels=["milestone-submission", "M5", "passed"],
                pull_request=True,
            ),
        ],
        allowlist(),
        NOW,
    )

    grace = builder_for(snapshot, "Grace")
    assert grace["milestonesSubmitted"] == 1
    assert grace["milestonesPassed"] == 3
    assert grace["currentMilestone"] == 3


def test_m5_path_selects_phase_and_pending_path_is_explicit():
    path_a = issue(
        1,
        "Ada",
        "M5",
        statuses=("needs-improvement",),
        body="### Which path did you take?\n\nPath A — Predictive / ML",
    )
    path_b = issue(
        2,
        "Grace",
        "M5",
        statuses=("ready-for-review",),
        body="### Which path did you take?\n\nPath B — Advanced EDA & Stakeholder Track",
    )
    snapshot = build_builders_snapshot(
        [
            issue(10, "Ada", "M0"),
            issue(11, "Ada", "M1"),
            issue(12, "Ada", "M2"),
            issue(13, "Ada", "M3"),
            issue(14, "Ada", "M4"),
            path_a,
            issue(20, "Grace", "M0"),
            issue(21, "Grace", "M1"),
            issue(22, "Grace", "M2"),
            issue(23, "Grace", "M3"),
            issue(24, "Grace", "M4"),
            path_b,
        ],
        allowlist(),
        NOW,
    )

    assert builder_for(snapshot, "Ada")["phase"] == "Predictive"
    assert builder_for(snapshot, "Grace")["phase"] == "Non-Predictive"

    pending = build_builders_snapshot(
        [issue(1, "Linus", "M0"), issue(2, "Linus", "M1"),
         issue(3, "Linus", "M2"), issue(4, "Linus", "M3"),
         issue(5, "Linus", "M4")],
        allowlist(),
        NOW,
    )
    assert builder_for(pending, "Linus")["currentMilestone"] == 5
    assert builder_for(pending, "Linus")["phase"] == "Predictive / Alt Track"


def test_m6_pass_completes_the_builder():
    snapshot = build_builders_snapshot(
        [
            issue(1, "Ada", "M0"),
            issue(2, "Ada", "M1"),
            issue(3, "Ada", "M2"),
            issue(4, "Ada", "M3"),
            issue(5, "Ada", "M4"),
            issue(6, "Ada", "M5", body="### Which path did you take?\n\nPath A — Predictive / ML"),
            issue(7, "Ada", "M6"),
        ],
        allowlist(),
        NOW,
    )

    ada = builder_for(snapshot, "Ada")
    assert ada["status"] == "Completed"
    assert ada["milestonesPassed"] == 7
    assert ada["currentMilestone"] == 6
    assert ada["phase"] == "Packaging & Deployment"


def test_project_title_uses_latest_nonempty_submission_title():
    snapshot = build_builders_snapshot(
        [
            issue(1, "Ada", "M2", title="[M2] Ada — <Analytical Engine>"),
            issue(2, "Ada", "M3", title='[M3] Ada — "Notes"'),
            issue(3, "Ada", "M4", title="[M4] Ada"),
        ],
        allowlist(),
        NOW,
    )

    assert builder_for(snapshot, "Ada")["projectTopic"] == "Notes"
    assert project_title(issue(4, "Ada", title="[M2] Ada — <Engine>")) == "Engine"
    assert project_title(issue(5, "Ada", title="No milestone prefix")) == ""


def test_name_opt_out_uses_username_not_issue_body():
    snapshot = build_builders_snapshot(
        [
            issue(
                1,
                "Ada",
                "M0",
                body="### Builder Name\n\nAda Lovelace",
            )
        ],
        allowlist(name_opt_outs=["Ada"]),
        NOW,
    )

    assert builder_for(snapshot, "Ada")["name"] == "Ada"


def test_display_name_falls_back_to_issue_body_then_username():
    snapshot = build_builders_snapshot(
        [
            issue(
                1,
                "Grace",
                "M0",
                body="### Builder Name\n\nGrace Hopper",
            ),
            issue(2, "Linus", "M0", body=""),
        ],
        allowlist(display_names={}),
        NOW,
    )

    assert builder_for(snapshot, "Grace")["name"] == "Grace Hopper"
    assert builder_for(snapshot, "Linus")["name"] == "Linus"


def test_manual_status_override_can_mark_a_builder_dropped():
    snapshot = build_builders_snapshot(
        [issue(1, "Grace", "M0")],
        allowlist(status_overrides={"Grace": "Dropped"}),
        NOW,
    )

    assert builder_for(snapshot, "Grace")["status"] == "Dropped"


def test_at_risk_override_is_rejected_from_public_data():
    with pytest.raises(ValueError, match="Unsupported public status"):
        build_builders_snapshot(
            [issue(1, "Grace", "M0")],
            allowlist(status_overrides={"Grace": "At Risk"}),
            NOW,
        )


def test_active_week_is_clamped_to_the_program_window():
    assert active_week(datetime(2026, 6, 1, tzinfo=timezone.utc), date(2026, 6, 22)) == 1
    assert active_week(NOW, date(2026, 6, 22)) == 19
    assert active_week(datetime(2027, 1, 1, tzinfo=timezone.utc), date(2026, 6, 22)) == 24


def test_updated_at_uses_the_philippine_date():
    snapshot = build_builders_snapshot(
        [],
        allowlist(),
        datetime(2026, 10, 26, 16, 30, tzinfo=timezone.utc),
    )

    assert snapshot["updatedAt"] == "2026-10-27"


def test_naive_timestamps_are_treated_as_utc():
    snapshot = build_builders_snapshot(
        [],
        allowlist(),
        datetime(2026, 10, 26, 16, 30),
    )

    assert snapshot["updatedAt"] == "2026-10-27"


def test_output_reports_cohort_and_source():
    snapshot = build_builders_snapshot([], allowlist(), NOW)

    assert snapshot["cohort"] == "2026-A"
    assert snapshot["source"] == "GitHub milestone-submission issues + enrolled-participants.json"


def test_comparison_ignores_updated_at_but_detects_content_changes():
    snapshot = build_builders_snapshot([], allowlist(), NOW)
    existing = {
        **snapshot,
        "updatedAt": "2026-10-01",
    }

    assert not builders_changed(existing, snapshot)

    changed = {
        **snapshot,
        "builders": [*snapshot["builders"], {"name": "New Builder"}],
    }
    assert builders_changed(existing, changed)


def test_malformed_existing_snapshot_is_replaced():
    snapshot = build_builders_snapshot([], allowlist(), NOW)

    assert builders_changed(None, snapshot)
    assert builders_changed({}, snapshot)
    assert builders_changed({"builders": "not-a-list"}, snapshot)
