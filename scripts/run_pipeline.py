#!/usr/bin/env python3
"""Run the project pipeline in order, with no manual steps.

Run from the repository root:
    python scripts/run_pipeline.py                 # transform -> analysis-ready -> analysis -> dashboard
    python scripts/run_pipeline.py --with-ingest   # also download the raw data first (needs Kaggle credentials)

Steps
    1. scripts/ingest.py                         (only with --with-ingest) -> data/raw/
    2. scripts/transform.py                      -> data/processed/dpwh_flood_control_projects_cleaned.csv
    3. scripts/advanced_transform.py             -> data/processed/dpwh_flood_control_analysis_ready.csv
    4. scripts/analysis/m5_segmentation_kpis.py  -> data/processed/m5_*.csv, output/figures/m5_*.png
    5. scripts/build_dashboard.py                -> dashboard/index.html (published to GitHub Pages)

The notebooks in notebooks/ read these outputs; open them after the pipeline finishes.
"""
import argparse
import subprocess
import sys
from pathlib import Path

RAW_FILE = Path("data/raw/dpwh_flood_control_projects.csv")
STEPS = [
    ("Clean raw data", "scripts/transform.py"),
    ("Build analysis-ready data", "scripts/advanced_transform.py"),
    ("Segmentation, KPIs and review shortlist", "scripts/analysis/m5_segmentation_kpis.py"),
    ("Build the dashboard", "scripts/build_dashboard.py"),
]


def run(label: str, script: str) -> None:
    print(f"\n=== {label}: python {script}")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        sys.exit(f"Step failed: {script} (exit code {result.returncode})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--with-ingest", action="store_true", help="Download raw data from Kaggle first")
    args = parser.parse_args()
    if not Path("scripts").is_dir():
        sys.exit("Run this from the repository root: python scripts/run_pipeline.py")
    if args.with_ingest:
        run("Download raw data", "scripts/ingest.py")
    elif not RAW_FILE.exists():
        sys.exit(f"{RAW_FILE} not found. Run with --with-ingest or place the raw CSV there.")
    for label, script in STEPS:
        run(label, script)
    print("\nPipeline complete. Outputs: data/processed/, output/figures/ and dashboard/index.html")


if __name__ == "__main__":
    main()
