"""Guard against reintroducing a bot-applied `passed` label.

A label added with the default GITHUB_TOKEN does not trigger another workflow
run, so `milestone-verdict.yml` would never finalize it. The old M0 auto-pass
path was removed in cd2d1e9; keep it removed.
"""

import re
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[1] / "workflows"
PASSED_LABEL_PATTERN = re.compile(
    r"labels:\s*\[\s*['\"]passed['\"]\s*\]",
    re.IGNORECASE,
)
LOGIC_MODULE = "milestone_logic.js"
LOGIC_CONSUMERS = (
    "_milestone-evaluate.yml",
    "milestone-recheck.yml",
    "milestone-verdict.yml",
    "notify-reviewer.yml",
)


def test_no_workflow_applies_passed_label_directly():
    offenders = [
        path.name
        for path in WORKFLOWS.glob("*.yml")
        if PASSED_LABEL_PATTERN.search(path.read_text(encoding="utf-8"))
    ]

    assert not offenders, (
        "Workflows must not add the `passed` label with the default token; "
        f"finalization would not run: {offenders}"
    )


def test_credential_scan_runs_in_evaluation_and_before_pass():
    """Both the submission evaluation and the pass guard must call the scanner."""
    evaluate = (WORKFLOWS / "_milestone-evaluate.yml").read_text(encoding="utf-8")
    verdict = (WORKFLOWS / "milestone-verdict.yml").read_text(encoding="utf-8")

    assert "secret_scan.py" in evaluate, "evaluation must scan the submitted repo"
    assert "secret_scan.py" in verdict, "finalize-pass must scan the current default branch"
    assert "SECRETS_OK" in verdict, "finalize-pass must block on a credential hit"


def test_evaluation_cannot_ready_for_review_with_a_credential_hit():
    evaluate = (WORKFLOWS / "_milestone-evaluate.yml").read_text(encoding="utf-8")

    assert "results?.all_passed === true && secretsOk" in evaluate


def test_finalize_pass_guard_blocks_and_does_not_release():
    verdict = (WORKFLOWS / "milestone-verdict.yml").read_text(encoding="utf-8")

    assert "process.env.SECRETS_OK === 'false'" in verdict
    assert "removeLabels(issue.number, ['passed'])" in verdict
    assert "labels: ['needs-improvement']" in verdict
    assert "core.setOutput('waiting_issue_number', '')" in verdict


def test_secret_audit_pins_and_redacts_gitleaks():
    audit = (WORKFLOWS / "secret-audit.yml").read_text(encoding="utf-8")

    assert 'GITLEAKS_VERSION: "8.30.1"' in audit
    assert "linux_x64.tar.gz" in audit
    assert "GITLEAKS_SHA256" in audit
    assert "sha256sum --check" in audit
    assert "--redact" in audit


def test_workflows_use_shared_milestone_logic_module():
    """Policy parsing must come from the tested module, not inline copies."""
    for name in LOGIC_CONSUMERS:
        text = (WORKFLOWS / name).read_text(encoding="utf-8")
        assert LOGIC_MODULE in text, (
            f"{name} must require .github/scripts/{LOGIC_MODULE} instead of "
            "re-implementing milestone policy inline"
        )
