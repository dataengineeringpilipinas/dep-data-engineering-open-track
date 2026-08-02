"""
Structural checks for each DEP milestone.
Clones the builder repo at a specific commit and verifies required artifacts exist.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def check(name: str, passed: bool, hint: str = "") -> dict:
    return {"name": name, "passed": passed, "hint": hint}


def has_file(root: Path, *parts: str) -> bool:
    return (root / Path(*parts)).is_file()


def dir_has_real_files(root: Path, *parts: str) -> bool:
    """True if the directory exists and contains at least one non-.gitkeep file,
    searching subdirectories recursively."""
    d = root / Path(*parts)
    if not d.is_dir():
        return False
    return any(f.name != ".gitkeep" for f in d.rglob("*") if f.is_file())


def readme_has_content(root: Path, min_chars: int = 100) -> bool:
    readme = root / "README.md"
    if not readme.is_file():
        return False
    return len(readme.read_text(encoding="utf-8", errors="ignore").strip()) >= min_chars


def checks_m0(root: Path) -> list:
    return [
        check(
            "README.md exists",
            has_file(root, "README.md"),
            "Add a README.md to the root of your repo.",
        ),
        check(
            "README.md has meaningful content (≥100 chars)",
            readme_has_content(root),
            "Your README appears empty or too short. Describe your project problem and data source.",
        ),
    ]


def checks_m1(root: Path) -> list:
    return [
        check(
            "`data/raw/` directory exists",
            (root / "data" / "raw").is_dir(),
            "Create `data/raw/` in your repo (a `.gitkeep` placeholder is fine at this stage).",
        ),
        check(
            "`data/processed/` directory exists",
            (root / "data" / "processed").is_dir(),
            "Create `data/processed/` in your repo.",
        ),
        check(
            "`scripts/` directory exists",
            (root / "scripts").is_dir(),
            "Create a `scripts/` directory.",
        ),
        check(
            "`notebooks/` directory exists",
            (root / "notebooks").is_dir(),
            "Create a `notebooks/` directory.",
        ),
        check(
            "`requirements.txt` exists",
            has_file(root, "requirements.txt"),
            "Add a `requirements.txt` at the repo root, even if it lists only Python version for now.",
        ),
        check(
            "README.md has meaningful content (≥100 chars)",
            readme_has_content(root),
            "Expand your README to describe the problem, data source, and project goal.",
        ),
    ]


def checks_m2(root: Path) -> list:
    return [
        check(
            "`scripts/ingest.py` exists",
            has_file(root, "scripts", "ingest.py"),
            "Add `scripts/ingest.py` — this is your ingestion script.",
        ),
        check(
            "`data/raw/` contains at least one real data file",
            dir_has_real_files(root, "data", "raw"),
            "`data/raw/` is empty or only has `.gitkeep`. Run your ingestion script and commit the output.",
        ),
        check(
            "`requirements.txt` exists",
            has_file(root, "requirements.txt"),
            "Add or update `requirements.txt` with your ingestion dependencies.",
        ),
    ]


def checks_m3(root: Path) -> list:
    return [
        check(
            "`scripts/transform.py` exists",
            has_file(root, "scripts", "transform.py"),
            "Add `scripts/transform.py` — this is your transformation script.",
        ),
        check(
            "`data/processed/` contains at least one output file",
            dir_has_real_files(root, "data", "processed"),
            "`data/processed/` is empty. Run your transform script and commit the output.",
        ),
        check(
            "`requirements.txt` exists",
            has_file(root, "requirements.txt"),
            "Update `requirements.txt` with any new processing dependencies.",
        ),
    ]


def checks_m4(root: Path) -> list:
    notebooks_dir = root / "notebooks"
    has_notebook = (
        notebooks_dir.is_dir()
        and any(f.suffix == ".ipynb" for f in notebooks_dir.rglob("*.ipynb"))
    )
    return [
        check(
            "`notebooks/` contains at least one `.ipynb` file",
            has_notebook,
            "Add at least one Jupyter notebook to `notebooks/` with your analysis.",
        ),
        check(
            "`requirements.txt` exists",
            has_file(root, "requirements.txt"),
            "Update `requirements.txt` with analysis dependencies (e.g. pandas, matplotlib).",
        ),
    ]


def checks_m5(root: Path) -> list:
    notebooks_dir = root / "notebooks"
    has_notebook = (
        notebooks_dir.is_dir()
        and any(f.suffix == ".ipynb" for f in notebooks_dir.rglob("*.ipynb"))
    )
    req = root / "requirements.txt"
    req_has_content = req.is_file() and len(req.read_text().strip()) > 0
    return [
        check(
            "`requirements.txt` exists and has content",
            req_has_content,
            "Ensure `requirements.txt` lists all your project dependencies.",
        ),
        check(
            "`notebooks/` contains at least one `.ipynb` file",
            has_notebook,
            "Your analysis or model notebook should be in `notebooks/`.",
        ),
        check(
            "`data/processed/` contains at least one output file",
            dir_has_real_files(root, "data", "processed"),
            "Save processed/model outputs to `data/processed/` or `output/`.",
        ),
    ]


def checks_m6(root: Path) -> list:
    return [
        check(
            "`dashboard/index.html` exists",
            has_file(root, "dashboard", "index.html"),
            "Add `dashboard/index.html` — this is your deployable dashboard or report.",
        ),
        check(
            "`requirements.txt` exists",
            has_file(root, "requirements.txt"),
            "Ensure `requirements.txt` is present and up to date.",
        ),
        check(
            "README.md has meaningful content (≥100 chars)",
            readme_has_content(root),
            "Your README should include the live URL and a project summary.",
        ),
    ]


MILESTONE_CHECKS = {
    "M0": checks_m0,
    "M1": checks_m1,
    "M2": checks_m2,
    "M3": checks_m3,
    "M4": checks_m4,
    "M5": checks_m5,
    "M6": checks_m6,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--milestone", required=True, help="e.g. M0, M1, ... M6")
    parser.add_argument("--repo-path", required=True, help="Path to the cloned builder repo")
    parser.add_argument("--output-file", default="check_result.json")
    args = parser.parse_args()

    milestone = args.milestone.upper()
    root = Path(args.repo_path).resolve()

    if milestone not in MILESTONE_CHECKS:
        print(f"Unknown milestone: {milestone}", file=sys.stderr)
        sys.exit(1)

    checks = MILESTONE_CHECKS[milestone](root)
    passed_count = sum(1 for c in checks if c["passed"])
    result = {
        "milestone": milestone,
        "repo_path": str(root),
        "passed": passed_count,
        "total": len(checks),
        "all_passed": all(c["passed"] for c in checks),
        "checks": checks,
    }

    with open(args.output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"{milestone}: {passed_count}/{len(checks)} checks passed")
    if not result["all_passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
