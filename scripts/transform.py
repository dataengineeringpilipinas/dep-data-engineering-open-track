#!/usr/bin/env python3
"""Step 2 of the pipeline: clean the raw DPWH file (raw -> cleaned).

Run from the repository root:
    python scripts/transform.py

Input : data/raw/dpwh_flood_control_projects.csv
Output: data/processed/dpwh_flood_control_projects_cleaned.csv

What this step does (and does NOT do):
- renames columns to lowercase, with three readable names
  (project_id, district_engineering_office, contract_cost_php)
- strips whitespace from text columns
- converts money columns to numbers; text such as "MYCA with Project ID ..." or
  "Clustered with Contract ID ..." cannot be a number, so it becomes empty (NaN)
  and the original text is kept in a *_note column so nothing is lost
- converts the two date columns to real dates
- keeps every raw row and the source row order (no deduplication here;
  duplicate project IDs are handled in scripts/advanced_transform.py)
- leaves missing municipality values empty instead of inventing a value

Validation checks at the end stop the pipeline if the output is not what we expect.
Running it twice on the same raw file gives the same output file.
"""
import sys
from pathlib import Path

import pandas as pd

RAW_FILE = Path("data/raw/dpwh_flood_control_projects.csv")
PROCESSED_FILE = Path("data/processed/dpwh_flood_control_projects_cleaned.csv")

RENAME = {
    "projectid": "project_id",
    "districtengineeringoffice": "district_engineering_office",
    "contractcost": "contract_cost_php",
}
MONEY_COLUMNS = {
    "contract_cost_php": "contract_cost_note",
    "approvedbudgetforcontract": "approved_budget_note",
}
DATE_COLUMNS = ["actualcompletiondate", "startdate"]
REQUIRED_COLUMNS = {
    "project_id", "contractid", "fundingyear", "region", "province",
    "contractor", "contract_cost_php", "actualcompletiondate",
}


def profile(df: pd.DataFrame, stage: str) -> None:
    """Print a short profile: size and missing values per column."""
    print(f"\n--- {stage}: {len(df):,} rows, {df.shape[1]} columns")
    missing = df.isna().sum()
    missing = missing[missing > 0]
    print("Missing values:" if len(missing) else "Missing values: none")
    if len(missing):
        print(missing.to_string())


def clean(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # 1. Column names: lowercase, then three readable renames
    out.columns = [c.strip().lower().replace(" ", "_") for c in out.columns]
    out = out.rename(columns=RENAME)

    # 2. Text: strip leading/trailing spaces (missing values stay missing)
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].str.strip()

    # 3. Money: to numbers; keep any non-numeric text in a note column
    for col, note_col in MONEY_COLUMNS.items():
        numeric = pd.to_numeric(out[col], errors="coerce")
        out[note_col] = out[col].where(numeric.isna() & out[col].notna())
        out[col] = numeric

    # 4. Dates: to real dates (all raw dates are YYYY-MM-DD)
    for col in DATE_COLUMNS:
        out[col] = pd.to_datetime(out[col], format="%Y-%m-%d", errors="coerce")

    return out


def validate(raw: pd.DataFrame, cleaned: pd.DataFrame) -> None:
    """Stop the pipeline if the cleaned data breaks any of these rules."""
    problems = []
    if len(cleaned) != len(raw):
        problems.append(f"row count changed: raw={len(raw)}, cleaned={len(cleaned)}")
    missing_cols = sorted(REQUIRED_COLUMNS - set(cleaned.columns))
    if missing_cols:
        problems.append(f"missing required columns: {missing_cols}")
    if cleaned.duplicated().any():
        problems.append(f"{cleaned.duplicated().sum()} exact duplicate rows")
    if cleaned["project_id"].isna().any():
        problems.append("some rows have no project_id")
    if cleaned.duplicated(subset=["project_id", "contractid", "fundingyear"]).any():
        problems.append("(project_id, contractid, fundingyear) is not unique")
    if (cleaned["startdate"] > cleaned["actualcompletiondate"]).any():
        problems.append("some projects start after they were completed")
    for col in DATE_COLUMNS:
        if not pd.api.types.is_datetime64_any_dtype(cleaned[col]):
            problems.append(f"{col} is not a date column")
        elif cleaned[col].isna().any():
            problems.append(f"{col} has {cleaned[col].isna().sum()} values that are not valid dates")
    for col in MONEY_COLUMNS:
        if not pd.api.types.is_numeric_dtype(cleaned[col]):
            problems.append(f"{col} is not numeric")
        elif (cleaned[col] < 0).any():
            problems.append(f"{col} has negative values")
    if problems:
        sys.exit("Validation failed:\n  - " + "\n  - ".join(problems))

    print("\nValidation passed: same row count as raw, required columns present, no exact duplicates,")
    print("(project_id, contractid, fundingyear) unique, dates are dates and in order,")
    print("money columns are numeric and non-negative.")
    for col, note_col in MONEY_COLUMNS.items():
        print(f"  {col}: {cleaned[note_col].notna().sum()} non-numeric values kept in {note_col}")
    dup_ids = cleaned["project_id"].duplicated().sum()
    print(f"  project_id: {dup_ids} repeated IDs (multi-year contracts), handled in advanced_transform.py")


def main() -> None:
    if not RAW_FILE.exists():
        sys.exit(f"Raw data file not found at {RAW_FILE}. Run scripts/ingest.py first.")

    raw = pd.read_csv(RAW_FILE)
    profile(raw, "Raw")
    cleaned = clean(raw)
    validate(raw, cleaned)
    profile(cleaned, "Cleaned")

    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(PROCESSED_FILE, index=False, date_format="%Y-%m-%d")
    print(f"\nSaved {PROCESSED_FILE}")


if __name__ == "__main__":
    main()
