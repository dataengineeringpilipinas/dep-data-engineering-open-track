"""
Guards for the repo-level fork-PR protections.
Run with: pytest .github/scripts/test_repo_guardrails.py -v
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODEOWNERS = ROOT / ".github" / "CODEOWNERS"
FORK_GUARD = ROOT / ".github" / "workflows" / "fork-pr-guard.yml"
CI = ROOT / ".github" / "workflows" / "ci.yml"


def test_codeowners_covers_protected_paths():
    text = CODEOWNERS.read_text(encoding="utf-8")

    for path in (
        ".github/",
        "01-foundations/",
        "02-data-collection/",
        "03-data-processing/",
        "04-analysis-and-insights/",
        "05-project-packaging/",
        "06-deployment/",
        "cohorts/",
        "docs/",
    ):
        assert f"/{path}" in text, path

    assert "@cancinoray" in text
    assert "@gkate78" in text


def test_fork_guard_uses_pull_request_target_and_base_code_only():
    text = FORK_GUARD.read_text(encoding="utf-8")

    assert "pull_request_target:" in text
    assert "fork_pr_guard.js" in text
    assert "persist-credentials: false" in text
    assert "sparse-checkout: .github/scripts" in text
    assert "github.event.pull_request.base.sha" in text
    assert "github.event.pull_request.head.sha" not in text


def test_ci_runs_fork_guard_tests():
    text = CI.read_text(encoding="utf-8")
    assert "test_fork_pr_guard.js" in text
