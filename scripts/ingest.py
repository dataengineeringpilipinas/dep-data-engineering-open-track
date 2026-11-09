#!/usr/bin/env python3
"""Step 1 of the pipeline: download the raw DPWH flood control dataset into data/raw.

Run from the repository root:
    python scripts/ingest.py

Kaggle credentials are needed. Use either:
  - environment variables KAGGLE_USERNAME and KAGGLE_KEY, or
  - the file ~/.kaggle/kaggle.json  (Windows: C:\\Users\\<you>\\.kaggle\\kaggle.json)
Never commit kaggle.json or your key to the repository.

This step only saves the raw file. It does not clean or change any values;
cleaning happens in scripts/transform.py.

After downloading, it writes data/raw/SOURCE.md with the source URL and the
download time, so the raw file always has its provenance next to it.
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DATASET_ID = "bwandowando/dpwh-flood-control-projects"
SOURCE_URL = f"https://www.kaggle.com/datasets/{DATASET_ID}"
OUTPUT_DIR = Path("data/raw")
RAW_FILE = OUTPUT_DIR / "dpwh_flood_control_projects.csv"
SOURCE_NOTE = OUTPUT_DIR / "SOURCE.md"


def has_credentials() -> bool:
    env_ok = bool(os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"))
    config_dir = Path(os.getenv("KAGGLE_CONFIG_DIR", Path.home() / ".kaggle"))
    return env_ok or (config_dir / "kaggle.json").is_file()


def write_source_note(row_count: int) -> None:
    downloaded = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    SOURCE_NOTE.write_text(
        "# Raw data source\n\n"
        f"- **File:** `{RAW_FILE.name}`\n"
        "- **Dataset:** DPWH Flood Control Projects (Kaggle, by bwandowando)\n"
        f"- **Source URL:** {SOURCE_URL}\n"
        "- **Method:** Kaggle API, `python scripts/ingest.py`\n"
        f"- **Downloaded:** {downloaded}\n"
        f"- **Rows:** {row_count:,}\n"
        "- **Format:** CSV, one row per project record\n\n"
        "This file is raw and unmodified. Do not edit it by hand.\n",
        encoding="utf-8",
    )


def run_ingestion() -> None:
    if not has_credentials():
        sys.exit(
            "Kaggle credentials are missing. Set KAGGLE_USERNAME and KAGGLE_KEY, "
            "or create ~/.kaggle/kaggle.json."
        )

    # Imported here so the error above is shown before the kaggle package
    # tries (and fails) to authenticate on import.
    from kaggle.api.kaggle_api_extended import KaggleApi

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    api = KaggleApi()
    api.authenticate()

    print(f"Downloading '{DATASET_ID}' into {OUTPUT_DIR}/ ...")
    api.dataset_download_files(DATASET_ID, path=str(OUTPUT_DIR), unzip=True)

    if not RAW_FILE.exists():
        sys.exit(f"Download finished but {RAW_FILE} was not found. Check the dataset files on Kaggle.")

    with RAW_FILE.open(encoding="utf-8") as f:
        row_count = sum(1 for _ in f) - 1  # minus the header line
    write_source_note(row_count)
    print(f"Saved {RAW_FILE} ({row_count:,} rows) and {SOURCE_NOTE}")


if __name__ == "__main__":
    run_ingestion()
