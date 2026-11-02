"""Backward-compatible wrapper for the ingestion script.

Use scripts/ingest.py going forward. This file remains to avoid breaking older
review notes or references that still call `python scripts/injest.py`.
"""

import warnings

from ingest import run_ingestion

if __name__ == "__main__":
    warnings.warn(
        "scripts/injest.py is deprecated; use scripts/ingest.py instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    run_ingestion()
