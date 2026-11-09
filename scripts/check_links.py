#!/usr/bin/env python3
"""Final QA: check that relative links and images in README.md and docs/*.md point to files that exist,
and that the README contains the live dashboard URL.

Run from the repository root:  python scripts/check_links.py
"""
import re
import sys
from pathlib import Path

LIVE_URL = "https://michaelbacus-lab.github.io/dep-data-engineering-open-track/"
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def main() -> None:
    files = [Path("README.md"), *sorted(Path("docs").glob("*.md")), *sorted(Path(".").glob("*/README.md")),
             Path("data/raw/SOURCE.md"), Path("notebooks/data_transform_report.md")]
    problems = []
    for f in files:
        if not f.exists():
            continue
        for target in LINK.findall(f.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = (f.parent / target.split("#")[0]).resolve()
            if not path.exists():
                problems.append(f"{f}: missing file for link '{target}'")
    for required in ["dashboard/index.html", "requirements.txt", "docs/stakeholder_brief.pdf",
                     ".github/workflows/pages.yml", "data/raw/SOURCE.md"]:
        if not Path(required).exists():
            problems.append(f"missing required file: {required}")
    readme = Path("README.md").read_text(encoding="utf-8") if Path("README.md").exists() else ""
    if LIVE_URL not in readme:
        problems.append("README.md does not contain the live dashboard URL")
    print("\n".join(problems) if problems else "All checks passed: links resolve and the live URL is in the README.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
