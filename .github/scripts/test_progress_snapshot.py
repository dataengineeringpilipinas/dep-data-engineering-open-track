from progress_snapshot import build_snapshot, snapshot_changed


def issue(number: int, **overrides):
    payload = {
        "number": number,
        "title": f"Issue {number}",
        "labels": [{"name": "milestone-submission"}],
    }
    payload.update(overrides)
    return payload


def test_build_snapshot_sorts_issues_by_number():
    snapshot = build_snapshot(
        [issue(10), issue(2), issue(7)],
        generated_at="2026-10-19T00:00:00Z",
    )

    assert snapshot["generated_at"] == "2026-10-19T00:00:00Z"
    assert [item["number"] for item in snapshot["issues"]] == [2, 7, 10]


def test_comparison_ignores_generated_at_and_input_order():
    existing = {
        "generated_at": "2026-08-02T20:57:12Z",
        "issues": [issue(2), issue(10)],
    }

    assert not snapshot_changed(existing, [issue(10), issue(2)])


def test_comparison_detects_label_changes():
    existing = {"issues": [issue(2, labels=[{"name": "milestone-submission"}])]}

    updated = [issue(2, labels=[{"name": "milestone-submission"}, {"name": "passed"}])]

    assert snapshot_changed(existing, updated)


def test_comparison_detects_new_and_removed_issues():
    existing = {"issues": [issue(2)]}

    assert snapshot_changed(existing, [issue(2), issue(3)])
    assert snapshot_changed(existing, [])


def test_missing_or_malformed_existing_snapshot_is_replaced():
    assert snapshot_changed(None, [issue(2)])
    assert snapshot_changed({}, [issue(2)])
    assert snapshot_changed({"issues": "not-a-list"}, [issue(2)])
