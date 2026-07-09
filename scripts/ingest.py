"""
Phase 2 — Data Ingestion
Replace this template with your own ingestion logic.
"""

import os

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def ingest():
    # TODO: replace with your ingestion logic
    # Examples:
    #   - Download a CSV from a URL using requests
    #   - Call an API and save the JSON response
    #   - Read a manually downloaded file and copy it here
    raise NotImplementedError("Add your ingestion logic here.")


if __name__ == "__main__":
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    ingest()
    print("Ingestion complete. Check data/raw/ for output.")
