"""
Detect committed credential files and high-confidence credential patterns.

Filename checks come first by design: a legacy Kaggle API key is 32 hex
characters with no prefix, so a pattern scanner can miss it, while the file
that carries it (`kaggle.json`) has a stable name. Content checks then catch
credentials hardcoded in scripts, notebooks, and config files.

Only paths and rule names are reported; file contents are never printed.
This is not a replacement for a full secret scanner such as gitleaks, but it
covers the file names and token shapes most likely in a data project.

Run with: python secret_scan.py --repo-path <dir> [--git-repo <dir> --git-ref <ref>]
"""

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

# Example env files are templates, not credentials.
ALLOWED_ENV_FILES = {".env.example", ".env.sample", ".env.template"}

SECRET_BASENAMES = {
    "kaggle.json",
    ".env",
    "credentials.json",
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
    "application_default_credentials.json",
}

SECRET_PATTERNS = (
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.jks",
    "*.keystore",
    "*.ppk",
    "service-account*.json",
    "firebase-adminsdk*.json",
    "client_secret*.json",
)

# Credential stores whose file name is too generic to match anywhere.
SECRET_PATH_SUFFIXES = (
    ".aws/credentials",
    ".docker/config.json",
    ".streamlit/secrets.toml",
)

# Vendor and cache directories that never belong to a builder's own work.
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
}

MAX_CONTENT_BYTES = 1024 * 1024  # 1 MiB; credentials live in small files.
PLACEHOLDER_MARKERS = (
    "example",
    "placeholder",
    "redacted",
    "dummy",
    "xxxx",
    "your-",
    "your_",
    "<",
    ">",
)

# High-confidence token shapes. Generic 32-hex strings are deliberately absent:
# they match hashes and legacy Kaggle keys, which the filename rule catches.
CONTENT_PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY(?: BLOCK)?-----")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    (
        "github-token",
        re.compile(
            r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b"
            r"|\bgithub_pat_[A-Za-z0-9_]{22,}\b"
        ),
    ),
    ("slack-token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("stripe-secret-key", re.compile(r"\b[rs]k_live_[0-9A-Za-z]{20,}\b")),
    ("openai-api-key", re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("anthropic-api-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("huggingface-token", re.compile(r"\bhf_[A-Za-z0-9]{30,}\b")),
    ("npm-token", re.compile(r"\bnpm_[A-Za-z0-9]{36}\b")),
    ("pypi-token", re.compile(r"\bpypi-[A-Za-z0-9_-]{50,}\b")),
    ("sendgrid-api-key", re.compile(r"\bSG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}\b")),
    ("databricks-token", re.compile(r"\bdapi[0-9a-f]{32}\b")),
    ("google-oauth-client-secret", re.compile(r"\bGOCSPX-[A-Za-z0-9_-]{28}\b")),
    ("azure-storage-key", re.compile(r"\bAccountKey=[A-Za-z0-9+/=]{40,}")),
)

GIT_TIMEOUT_SECONDS = 30


def is_secret_name(name: str) -> bool:
    """True when a file name matches a known credential-file rule."""
    lower = name.lower()
    if lower in ALLOWED_ENV_FILES:
        return False
    return (
        lower in SECRET_BASENAMES
        or lower.startswith(".env.")
        or any(fnmatch.fnmatchcase(lower, pattern) for pattern in SECRET_PATTERNS)
    )


def is_secret_path(relative: str) -> bool:
    """True when a repo-relative path is a known credential store."""
    lower = relative.lower()
    return any(
        lower == suffix or lower.endswith("/" + suffix)
        for suffix in SECRET_PATH_SUFFIXES
    )


def is_placeholder(value: str) -> bool:
    """Skip documentation examples such as AKIA...EXAMPLE and ghp_xxxx."""
    lower = value.lower()
    return any(marker in lower for marker in PLACEHOLDER_MARKERS)


def scan_text(text: str) -> list:
    """Return rule names whose high-confidence pattern matches the text."""
    rules = set()
    for rule, pattern in CONTENT_PATTERNS:
        for match in pattern.finditer(text):
            if not is_placeholder(match.group(0)):
                rules.add(rule)
                break
    return sorted(rules)


def scan_file_content(path: Path) -> list:
    """Return rule names for a file's contents, skipping binaries and large files."""
    try:
        if path.stat().st_size > MAX_CONTENT_BYTES:
            return []
        data = path.read_bytes()
    except OSError:
        return []
    if b"\x00" in data[:4096]:
        return []
    return scan_text(data.decode("utf-8", errors="ignore"))


def find_secret_matches(root: Path) -> list:
    """Return path/rule matches for a checked-out tree."""
    matches = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            relative = path.relative_to(root).as_posix()
            if is_secret_name(name) or is_secret_path(relative):
                matches.add((relative, "filename", "filename"))
                continue
            for rule in scan_file_content(path):
                matches.add((relative, rule, "content"))
    return [
        {"path": path, "rule": rule, "kind": kind}
        for path, rule, kind in sorted(matches)
    ]


def find_secret_files(root: Path) -> list:
    """Return repo-relative paths of files containing credentials."""
    return sorted({match["path"] for match in find_secret_matches(root)})


def git_tree_files(repo: Path, ref: str) -> list:
    """Return every tracked path at ref without checking the tree out."""
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", "--full-tree", ref],
        capture_output=True,
        text=True,
        timeout=GIT_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git ls-tree failed for {ref}")
    return [line for line in result.stdout.splitlines() if line.strip()]


def find_secret_files_in_git(repo: Path, ref: str) -> list:
    """Return credential file names tracked at ref, using tree entries only."""
    return sorted({
        path
        for path in git_tree_files(repo, ref)
        if is_secret_name(PurePosixPath(path).name) or is_secret_path(path)
    })


def scan(repo_path: str = "", git_repo: str = "", git_ref: str = "") -> dict:
    """Scan a working tree and/or a git ref, returning a paths-only report."""
    matches = set()
    errors = []

    if repo_path:
        root = Path(repo_path).resolve()
        if root.is_dir():
            for match in find_secret_matches(root):
                matches.add((match["path"], match["rule"], match["kind"]))
        else:
            errors.append(f"Repository path not found: {repo_path}")

    if git_repo and git_ref:
        repo = Path(git_repo).resolve()
        try:
            for path in find_secret_files_in_git(repo, git_ref):
                matches.add((path, "filename", "filename"))
        except (RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
            errors.append(str(exc))
    elif bool(git_repo) != bool(git_ref):
        errors.append("Both --git-repo and --git-ref are required to scan a git ref.")

    if not repo_path and not git_repo:
        errors.append("No scan source provided.")

    report = [
        {"path": path, "rule": rule, "kind": kind}
        for path, rule, kind in sorted(matches)
    ]
    return {
        "clean": not report,
        "findings": sorted({match["path"] for match in report}),
        "matches": report,
        "errors": errors,
    }


def write_output(path: str, result: dict) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"secrets_ok={'true' if result['clean'] else 'false'}\n")
        if result["errors"]:
            # GITHUB_OUTPUT values must stay on one line.
            message = "; ".join(result["errors"]).replace("\n", " ")
            f.write(f"secret_scan_error={message}\n")


def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-path", default="", help="Checked-out tree to scan")
    parser.add_argument("--git-repo", default="", help="Git repository to inspect")
    parser.add_argument("--git-ref", default="", help="Ref to inspect, e.g. origin/HEAD")
    parser.add_argument("--output-file", default="secret_result.json")
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))
    args = parser.parse_args(argv)

    result = scan(args.repo_path, args.git_repo, args.git_ref)

    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    if args.github_output:
        write_output(args.github_output, result)
    else:
        print(json.dumps(result, indent=2))

    if result["findings"]:
        print(
            f"Credential material found in: {', '.join(result['findings'])}",
            file=sys.stderr,
        )
        return 1
    if result["errors"]:
        print(f"Credential scan incomplete: {'; '.join(result['errors'])}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
