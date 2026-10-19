import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = ROOT / ".github/enrolled-participants.json"
BUILDERS = ROOT / "docs/data/builders.json"

EXPECTED_ADDED = {"rainer-r", "ksdizon", "aezhile", "credough", "froncoyz"}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def github_username(url):
    match = re.search(r"github\.com/([^/\s]+)", url or "", re.IGNORECASE)
    return match.group(1).lower() if match else ""


def test_participants_are_nonempty_and_unique():
    participants = load_json(ALLOWLIST)["participants"]

    assert participants
    assert all(isinstance(user, str) and user.strip() for user in participants)
    assert len(participants) == len({user.lower() for user in participants})
    assert not any(user.lower().startswith("github-username-") for user in participants)


def test_official_roster_users_are_allowlisted():
    allowlist = load_json(ALLOWLIST)
    participants = {user.lower() for user in allowlist["participants"]}
    builders = load_json(BUILDERS)["builders"]

    missing = [
        builder["name"]
        for builder in builders
        if github_username(builder.get("github")) not in participants
    ]

    assert not missing, f"Roster builders missing from allowlist: {missing}"


def test_resolved_usernames_are_not_left_in_missing_github():
    allowlist = load_json(ALLOWLIST)
    resolved_names = {
        builder["name"]
        for builder in load_json(BUILDERS)["builders"]
        if github_username(builder.get("github"))
    }

    stale = resolved_names.intersection(allowlist["_missing_github"])
    assert not stale, f"Resolved usernames still listed as missing: {stale}"


def test_issue_227_allowlist_gaps_are_closed():
    participants = {user.lower() for user in load_json(ALLOWLIST)["participants"]}

    assert EXPECTED_ADDED <= participants
    assert "connette" not in participants
