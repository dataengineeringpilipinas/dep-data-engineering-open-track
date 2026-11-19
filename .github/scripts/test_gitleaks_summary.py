"""
Behavioral tests for gitleaks_summary.py.
Run with: pytest .github/scripts/test_gitleaks_summary.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gitleaks_summary import load_report, render


def test_empty_report_has_no_findings():
    assert render([]) == "No findings."
    assert render({"Findings": []}) == "No findings."


def test_report_renders_paths_and_rules_only():
    report = [{
        "File": "scripts/ingest.py",
        "RuleID": "aws-access-token",
        "StartLine": 12,
        "Secret": "do-not-print",
        "Match": "also-do-not-print",
    }]
    output = render(report)
    assert "scripts/ingest.py" in output
    assert "aws-access-token" in output
    assert "12" in output
    assert "do-not-print" not in output
    assert "also-do-not-print" not in output


def test_dict_report_uses_findings_key():
    output = render({"Findings": [{
        "File": "scripts/push.py",
        "RuleID": "github-token",
        "StartLine": 3,
    }]})
    assert "scripts/push.py" in output
    assert "github-token" in output


def test_markdown_cells_are_sanitized():
    output = render([{
        "File": "we`ird|name\n.py",
        "RuleID": "rule|id",
        "StartLine": 1,
    }])
    assert "we'ird\\|name .py" in output
    assert "rule\\|id" in output


def test_missing_and_empty_reports_return_none(tmp_path):
    assert load_report(tmp_path / "missing.json") is None
    empty = tmp_path / "empty.json"
    empty.write_text("")
    assert load_report(empty) is None


def test_unreadable_report_is_reported(tmp_path):
    path = tmp_path / "gitleaks.json"
    path.write_text("{")
    assert load_report(path) == "unreadable"
