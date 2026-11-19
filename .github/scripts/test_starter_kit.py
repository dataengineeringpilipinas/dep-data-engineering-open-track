"""
Tests for the builder-facing secret-prevention files.
Run with: pytest .github/scripts/test_starter_kit.py -v
"""

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STARTER = REPO_ROOT / "cohorts" / "starter-kit"


def git_ignored(root: Path, relative: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(root), "check-ignore", "-q", relative]
    ).returncode == 0


def test_starter_kit_gitignore_ignores_credentials(tmp_path):
    shutil.copy(STARTER / ".gitignore", tmp_path / ".gitignore")
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True)

    for relative in (
        "kaggle.json",
        ".env",
        ".env.local",
        ".aws/credentials",
        ".streamlit/secrets.toml",
        "service-account-prod.json",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x")

    for relative in (
        ".env.example",
        "scripts/ingest.py",
        "README.md",
        "data/raw/data.csv",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x")

    for relative in (
        "kaggle.json",
        ".env",
        ".env.local",
        ".aws/credentials",
        ".streamlit/secrets.toml",
        "service-account-prod.json",
    ):
        assert git_ignored(tmp_path, relative), relative

    for relative in (
        ".env.example",
        "scripts/ingest.py",
        "README.md",
        "data/raw/data.csv",
    ):
        assert not git_ignored(tmp_path, relative), relative


def test_m2_form_mentions_credentials():
    text = (REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "milestone-m2.yml").read_text(
        encoding="utf-8"
    )
    assert "secret scanning" in text
    assert "push protection" in text
    assert "kaggle.json" in text


def test_starter_kit_readme_mentions_secret_scanning():
    text = (STARTER / "README.md").read_text(encoding="utf-8")
    assert "secret scanning" in text
    assert "push protection" in text


def test_milestone_checklist_mentions_credentials():
    text = (REPO_ROOT / "docs" / "MILESTONE_CHECKLIST.md").read_text(encoding="utf-8")
    assert "Never commit credentials" in text
