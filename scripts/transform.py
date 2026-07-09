"""
Phase 3 — Data Transformation
Replace this template with your own transformation logic.
"""

import os

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def transform():
    # TODO: replace with your transformation logic
    # Examples:
    #   - Load raw CSV, clean column names, drop nulls, save to processed/
    #   - Run SQL queries against a local SQLite database
    #   - Merge multiple raw files into one clean dataset
    raise NotImplementedError("Add your transformation logic here.")


if __name__ == "__main__":
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    transform()
    print("Transformation complete. Check data/processed/ for output.")
