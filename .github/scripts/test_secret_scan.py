"""
Behavioral tests for secret_scan.py.
Run with: pytest .github/scripts/test_secret_scan.py -v
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from secret_scan import (
    find_secret_files,
    find_secret_files_in_git,
    find_secret_matches,
    is_secret_name,
    is_secret_path,
    scan,
)


# ---------------------------------------------------------------------------
# Filename rules
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", [
    "kaggle.json",
    ".env",
    ".env.local",
    ".env.production",
    "credentials.json",
    "service-account.json",
    "service-account-prod.json",
    "firebase-adminsdk-abc.json",
    "client_secret_123.json",
    "application_default_credentials.json",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    ".netrc",
    ".pgpass",
    ".pypirc",
    ".npmrc",
    ".git-credentials",
    "secrets.toml",
    "id_rsa.pem",
    "server.key",
    "client.p12",
    "client.pfx",
    "keystore.jks",
    "key.ppk",
])
def test_known_credential_filenames_are_flagged(name):
    assert is_secret_name(name)


@pytest.mark.parametrize("name", [
    ".env.example",
    ".env.sample",
    ".env.template",
    "readme.md",
    "requirements.txt",
    "data.json",
    "analysis.ipynb",
    ".envrc",
    "id_rsa.pub",
])
def test_safe_filenames_are_allowed(name):
    assert not is_secret_name(name)


def test_path_specific_credential_stores_are_flagged(tmp_path):
    for relative in (".aws/credentials", ".docker/config.json"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")
    assert find_secret_files(tmp_path) == [".aws/credentials", ".docker/config.json"]


def test_secret_path_matching_uses_suffixes():
    assert is_secret_path(".aws/credentials")
    assert is_secret_path("home/.aws/credentials")
    assert not is_secret_path("docs/aws/credentials.md")


def test_matching_is_case_insensitive():
    assert is_secret_name("Kaggle.JSON")
    assert is_secret_name(".ENV.Local")
    assert is_secret_name("Service-Account.json")


# ---------------------------------------------------------------------------
# Working-tree scans
# ---------------------------------------------------------------------------

def test_clean_tree_returns_no_findings(tmp_path):
    (tmp_path / "README.md").write_text("hello")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "raw.csv").write_text("a,b\n1,2")
    assert find_secret_files(tmp_path) == []


def test_kaggle_json_is_found_nested(tmp_path):
    nested = tmp_path / "notebooks" / "kaggle"
    nested.mkdir(parents=True)
    (nested / "kaggle.json").write_text('{"key": "secret"}')
    assert find_secret_files(tmp_path) == ["notebooks/kaggle/kaggle.json"]


def test_all_filename_rules_are_reported(tmp_path):
    (tmp_path / ".env").write_text("TOKEN=secret")
    (tmp_path / ".env.local").write_text("TOKEN=secret")
    (tmp_path / "credentials.json").write_text("{}")
    (tmp_path / "service-account-prod.json").write_text("{}")
    (tmp_path / "server.pem").write_text("...")
    (tmp_path / "server.key").write_text("...")
    assert find_secret_files(tmp_path) == [
        ".env",
        ".env.local",
        "credentials.json",
        "server.key",
        "server.pem",
        "service-account-prod.json",
    ]


def test_env_example_is_allowed_but_env_local_is_not(tmp_path):
    (tmp_path / ".env.example").write_text("TOKEN=")
    (tmp_path / ".env.sample").write_text("TOKEN=")
    (tmp_path / ".env.template").write_text("TOKEN=")
    (tmp_path / ".env.local").write_text("TOKEN=secret")
    assert find_secret_files(tmp_path) == [".env.local"]


def test_git_directory_is_ignored(tmp_path):
    git_dir = tmp_path / ".git" / "hooks"
    git_dir.mkdir(parents=True)
    (git_dir / "credentials.json").write_text("{}")
    assert find_secret_files(tmp_path) == []


# ---------------------------------------------------------------------------
# Git-ref scans
# ---------------------------------------------------------------------------

def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def make_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    return repo


def test_git_ref_scan_finds_tracked_credential(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "README.md").write_text("hello")
    (repo / "kaggle.json").write_text('{"key": "secret"}')
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "add files")
    assert find_secret_files_in_git(repo, "HEAD") == ["kaggle.json"]


def test_git_ref_scan_ignores_untracked_credential(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "README.md").write_text("hello")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "readme")
    (repo / "kaggle.json").write_text('{"key": "secret"}')
    assert find_secret_files_in_git(repo, "HEAD") == []


def test_git_ref_scan_rejects_missing_ref(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "README.md").write_text("hello")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "readme")
    with pytest.raises(RuntimeError):
        find_secret_files_in_git(repo, "does-not-exist")


# ---------------------------------------------------------------------------
# Content rules
# ---------------------------------------------------------------------------

def write_file(root, relative, content):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


CONTENT_CASES = [
    ("scripts/ingest.py", "AKIA" + "A" * 16, "aws-access-key"),
    ("scripts/load.py", "AIza" + "A" * 35, "google-api-key"),
    ("scripts/push.py", "ghp_" + "A" * 36, "github-token"),
    ("scripts/slack.py", "xoxb-" + "A" * 12, "slack-token"),
    ("scripts/pay.py", "sk_live_" + "A" * 24, "stripe-secret-key"),
    ("scripts/llm.py", "sk-proj-" + "A" * 24, "openai-api-key"),
    ("scripts/claude.py", "sk-ant-" + "A" * 24, "anthropic-api-key"),
    ("scripts/hf.py", "hf_" + "A" * 30, "huggingface-token"),
    ("scripts/npm.py", "npm_" + "A" * 36, "npm-token"),
    ("scripts/pypi.py", "pypi-" + "A" * 50, "pypi-token"),
    ("scripts/mail.py", "SG." + "A" * 22 + "." + "A" * 43, "sendgrid-api-key"),
    ("scripts/db.py", "dapi" + "0123456789abcdef" * 2, "databricks-token"),
    ("scripts/oauth.py", "GOCSPX-" + "A" * 28, "google-oauth-client-secret"),
    ("config/azure.py", "AccountKey=" + "A" * 44, "azure-storage-key"),
    ("notes.txt", "-----BEGIN RSA PRIVATE KEY-----", "private-key"),
]


@pytest.mark.parametrize("relative,content,rule", CONTENT_CASES)
def test_content_patterns_are_flagged(tmp_path, relative, content, rule):
    write_file(tmp_path, relative, content)
    result = scan(repo_path=str(tmp_path))
    assert result["clean"] is False
    assert result["findings"] == [relative]
    assert {"path": relative, "rule": rule, "kind": "content"} in result["matches"]
    assert content not in json.dumps(result)


def test_documentation_placeholders_are_ignored(tmp_path):
    write_file(
        tmp_path,
        "README.md",
        "AWS key: AKIAIOSFODNN7EXAMPLE\nGitHub token: ghp_" + "x" * 36,
    )
    assert find_secret_files(tmp_path) == []


def test_binary_files_are_not_content_scanned(tmp_path):
    (tmp_path / "blob.bin").write_bytes(b"\x00" + b"AKIA" + b"A" * 16)
    assert find_secret_files(tmp_path) == []


def test_filename_match_skips_content_scan(tmp_path):
    write_file(tmp_path, ".env", "AWS_KEY=AKIA" + "A" * 16)
    result = scan(repo_path=str(tmp_path))
    assert result["findings"] == [".env"]
    assert [match["rule"] for match in result["matches"]] == ["filename"]


def test_find_secret_matches_returns_paths_and_rules(tmp_path):
    write_file(tmp_path, "scripts/key.py", "AKIA" + "A" * 16)
    assert find_secret_matches(tmp_path) == [
        {"path": "scripts/key.py", "rule": "aws-access-key", "kind": "content"}
    ]


# ---------------------------------------------------------------------------
# scan() result shape
# ---------------------------------------------------------------------------

def test_scan_reports_clean_result(tmp_path):
    (tmp_path / "README.md").write_text("hello")
    result = scan(repo_path=str(tmp_path))
    assert result == {"clean": True, "findings": [], "matches": [], "errors": []}


def test_scan_reports_findings(tmp_path):
    (tmp_path / "kaggle.json").write_text("{}")
    result = scan(repo_path=str(tmp_path))
    assert result["clean"] is False
    assert result["findings"] == ["kaggle.json"]
    assert result["matches"] == [
        {"path": "kaggle.json", "rule": "filename", "kind": "filename"}
    ]
    assert result["errors"] == []


def test_scan_reports_missing_path_as_error():
    result = scan(repo_path="/definitely/not/a/repo")
    assert result["clean"] is True
    assert result["errors"]
