#!/usr/bin/env python3
"""Download the raw DPWH flood control dataset into data/raw.

Run from the repository root:
    python scripts/ingest.py

Set Kaggle credentials before running:
    export KAGGLE_USERNAME="your_username"
    export KAGGLE_KEY="your_api_key"

The script also accepts credentials from ~/.kaggle/kaggle.json if present.
"""

import os
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

DATASET_ID = "bwandowando/dpwh-flood-control-projects"
OUTPUT_DIR = Path("data/raw")


def run_ingestion() -> None:
    """Download and unzip the Kaggle dataset into the raw-data folder."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    username = os.getenv("KAGGLE_USERNAME")
    key = os.getenv("KAGGLE_KEY")

    if not username or not key:
        raise EnvironmentError(
            "Kaggle credentials are missing. Export KAGGLE_USERNAME and KAGGLE_KEY "
            "before running this script, or create ~/.kaggle/kaggle.json."
        )

    api = KaggleApi()
    api.authenticate()

    print(f"📥 Downloading dataset '{DATASET_ID}' into {OUTPUT_DIR}...")
    api.dataset_download_files(DATASET_ID, path=str(OUTPUT_DIR), unzip=True)

    print("✅ Extraction complete. Downloaded files:")
    for file_path in sorted(OUTPUT_DIR.glob("*")):
        print(f"   📄 {file_path.name}")


if __name__ == "__main__":
    run_ingestion()
