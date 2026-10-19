"""
Behavioral tests for clone_snapshot.py.
Run with: pytest .github/scripts/test_clone_snapshot.py -v
"""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from clone_snapshot import (
    CLONE_ERROR,
    INVALID_ERROR,
    NOT_FOUND_ERROR,
    SHORT_SHA_ERROR,
    clone_snapshot,
    main,
)


def run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def commit(repo: Path, filename: str) -> str:
    (repo / filename).write_text(filename, encoding="utf-8")
    run_git(repo, "add", filename)
    run_git(repo, "commit", "-q", "-m", filename)
    return run_git(repo, "rev-parse", "HEAD").stdout.strip()


@pytest.fixture
def source_repo(tmp_path):
    repo = tmp_path / "source"
    repo.mkdir()
    run_git(repo, "init", "-q")
    run_git(repo, "config", "user.email", "test@example.com")
    run_git(repo, "config", "user.name", "Test User")
    # Emulate GitHub, which serves unadvertised objects for full SHAs.
    run_git(repo, "config", "uploadpack.allowAnySHA1InWant", "true")
    return repo


def clone_url(repo: Path) -> str:
    return repo.resolve().as_uri()


def test_clones_full_sha_for_orphaned_commit(tmp_path, source_repo):
    first = commit(source_repo, "first.txt")
    orphaned = commit(source_repo, "second.txt")
    run_git(source_repo, "reset", "--hard", first)

    dest = tmp_path / "builder-repo"
    ok, error = clone_snapshot(clone_url(source_repo), orphaned, dest)

    assert ok, error
    assert run_git(dest, "rev-parse", "HEAD").stdout.strip() == orphaned


def test_resolves_short_sha_when_commit_is_reachable(tmp_path, source_repo):
    submitted = commit(source_repo, "first.txt")

    dest = tmp_path / "builder-repo"
    ok, error = clone_snapshot(clone_url(source_repo), submitted[:7], dest)

    assert ok, error
    assert run_git(dest, "rev-parse", "HEAD").stdout.strip() == submitted


def test_short_sha_for_orphaned_commit_reports_specific_error(tmp_path, source_repo):
    first = commit(source_repo, "first.txt")
    orphaned = commit(source_repo, "second.txt")
    run_git(source_repo, "reset", "--hard", first)

    dest = tmp_path / "builder-repo"
    ok, error = clone_snapshot(clone_url(source_repo), orphaned[:7], dest)

    assert not ok
    assert error == SHORT_SHA_ERROR
    assert "full 40-character hash" in error


def test_full_sha_for_missing_commit_reports_not_found(tmp_path, source_repo):
    commit(source_repo, "first.txt")

    dest = tmp_path / "builder-repo"
    ok, error = clone_snapshot(clone_url(source_repo), "0" * 40, dest)

    assert not ok
    assert error == NOT_FOUND_ERROR


def test_invalid_hash_is_rejected_without_cloning(tmp_path):
    dest = tmp_path / "builder-repo"
    ok, error = clone_snapshot("https://example.com/not-a-repo.git", "not-a-sha", dest)

    assert not ok
    assert error == INVALID_ERROR
    assert not dest.exists()


def test_unclonable_repo_reports_public_error(tmp_path):
    dest = tmp_path / "builder-repo"
    ok, error = clone_snapshot((tmp_path / "missing").as_uri(), "a" * 7, dest)

    assert not ok
    assert error == CLONE_ERROR


def test_main_writes_success_to_github_output(tmp_path, source_repo):
    submitted = commit(source_repo, "first.txt")
    output = tmp_path / "github_output"

    rc = main([
        "--repo-url", clone_url(source_repo),
        "--commit-hash", submitted[:7],
        "--dest", str(tmp_path / "builder-repo"),
        "--github-output", str(output),
    ])

    assert rc == 0
    assert output.read_text(encoding="utf-8") == "clone_ok=true\n"


def test_main_writes_failure_and_error_to_github_output(tmp_path, source_repo):
    first = commit(source_repo, "first.txt")
    orphaned = commit(source_repo, "second.txt")
    run_git(source_repo, "reset", "--hard", first)
    output = tmp_path / "github_output"

    rc = main([
        "--repo-url", clone_url(source_repo),
        "--commit-hash", orphaned[:7],
        "--dest", str(tmp_path / "builder-repo"),
        "--github-output", str(output),
    ])

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    assert "clone_ok=false" in text
    assert f"clone_error={SHORT_SHA_ERROR}" in text
