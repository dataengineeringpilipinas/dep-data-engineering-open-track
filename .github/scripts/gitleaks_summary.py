"""
Render a gitleaks JSON report as a Markdown summary.

Only file paths, rule IDs, and line numbers are printed. Match and Secret
fields are never included.
"""

import argparse
import json
from pathlib import Path


def cell(value) -> str:
    """Make a value safe for a Markdown table cell."""
    return (
        str(value)
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("`", "'")
        .replace("|", "\\|")
    )


def render(report) -> str:
    if isinstance(report, dict):
        report = report.get("Findings", [])
    if not report:
        return "No findings."

    lines = ["| File | Rule | Line |", "| --- | --- | --- |"]
    for finding in report:
        if not isinstance(finding, dict):
            continue
        lines.append(
            f"| `{cell(finding.get('File', ''))}` "
            f"| `{cell(finding.get('RuleID', ''))}` "
            f"| {finding.get('StartLine', '')} |"
        )
    return "\n".join(lines)


def load_report(path: Path):
    """Return the parsed report, None when absent/empty, or 'unreadable'."""
    if not path.is_file() or path.stat().st_size == 0:
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return "unreadable"


def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", nargs="?", default="gitleaks.json")
    args = parser.parse_args(argv)

    report = load_report(Path(args.report))
    if report is None:
        print("gitleaks did not produce a report.")
    elif report == "unreadable":
        print("gitleaks report could not be parsed.")
    else:
        print(render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
