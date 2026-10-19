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


def test_workflows_use_shared_milestone_logic_module():
    """Policy parsing must come from the tested module, not inline copies."""
    for name in LOGIC_CONSUMERS:
        text = (WORKFLOWS / name).read_text(encoding="utf-8")
        assert LOGIC_MODULE in text, (
            f"{name} must require .github/scripts/{LOGIC_MODULE} instead of "
            "re-implementing milestone policy inline"
        )
