from pathlib import Path

import pandas as pd
from IPython.display import display

# File Paths (relative to root of cloned repo in Colab)
RAW_FILE = Path("data/raw/dpwh_flood_control_projects.csv")
PROCESSED_FILE = Path("data/processed/dpwh_flood_control_projects_cleaned.csv")


def profile_dataset(df: pd.DataFrame, stage: str = "Raw") -> None:
    """Prints diagnostic structural metrics and missing value statistics."""
    print(f"\n=================== {stage} Data Profile ===================")
    print(f"Shape: {df.shape[0]:,} rows, {df.shape[1]} columns")
    print("\n--- Summary Info ---")
    df.info(memory_usage="deep")
    print("\n--- Missing Values Count ---")
    print(df.isnull().sum())
    print("\n--- Data Sample Preview ---")
    display(df.head(5))
    print("============================================================\n")


def clean_dpwh_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans, standardizes, and formats DPWH flood control data."""
    df_clean = df.copy()

    # 1. Standardize column names to lowercase snake_case
    df_clean.columns = [col.strip().lower().replace(" ", "_") for col in df_clean.columns]

    # Map raw schema to explicit standardized column names
    rename_mapping = {
        "projectid": "ProjectId",
        "districtengineeringoffice": "DistrictEngineeringOffice",
        "contractcost": "ContractCost",
        "contractor": "Contractor",
        "province": "Province",
        "region": "Region",
        "municipality": "Municipality",
        "approvedbudgetforcontract": "ApprovedBudgetForContract",
        "fundingyear": "FundingYear",
        "contractid": "ContractId",
        "completiondate": "CompletionDate",
        "startdate": "StartDate",
        "typeofwork": "TypeOfWork",
        "projecttitle": "ProjectTitle",
    }
    df_clean.rename(columns=rename_mapping, inplace=True)

    # 2. Clean text columns
    for col in df_clean.select_dtypes(include=["object"]).columns:
        df_clean[col] = df_clean[col].astype(str).str.strip()
        df_clean[col] = df_clean[col].replace(["nan", "None", "", "N/A"], "Unknown")

    # 3. Convert numeric values safely
    numeric_cols = [
        "ApprovedBudgetForContract",
        "ContractCost",
        "FundingYear",
    ]
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    # 4. Remove duplicate rows and keep deterministic ordering
    initial_rows = len(df_clean)
    df_clean = df_clean.drop_duplicates().copy()
    deduped_rows = initial_rows - len(df_clean)
    if deduped_rows > 0:
        print(f"🧹 Removed {deduped_rows:,} exact duplicate rows.")

    if {"ProjectId", "ContractId", "FundingYear"}.issubset(df_clean.columns):
        df_clean = df_clean.sort_values(
            by=["ProjectId", "ContractId", "FundingYear"],
            kind="mergesort",
        ).reset_index(drop=True)

    return df_clean


def validate_cleaned_dataset(raw_df: pd.DataFrame, clean_df: pd.DataFrame) -> None:
    """Checks for structural integrity and reproducibility in the cleaned data."""
    if len(clean_df) != len(raw_df):
        raise ValueError(
            f"Row count mismatch: raw={len(raw_df)} but cleaned={len(clean_df)}"
        )

    key_cols = ["ProjectId", "ContractId", "FundingYear"]
    if all(col in clean_df.columns for col in key_cols):
        duplicate_keys = clean_df.duplicated(subset=key_cols).sum()
        if duplicate_keys > 0:
            raise ValueError(f"Duplicate key combinations found: {duplicate_keys}")

    required_cols = {"ProjectId", "ContractId", "FundingYear", "Region", "Province", "Contractor"}
    missing_cols = sorted(required_cols - set(clean_df.columns))
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    print("✅ Validation checks passed: row count matches source and keys remain unique.")


def main():
    if not RAW_FILE.exists():
        print(f"Error: Raw data file not found at {RAW_FILE}")
        return

    df_raw = pd.read_csv(RAW_FILE)
    profile_dataset(df_raw, "Raw")

    df_cleaned = clean_dpwh_dataset(df_raw)
    validate_cleaned_dataset(df_raw, df_cleaned)

    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    df_cleaned.to_csv(PROCESSED_FILE, index=False)
    print(f"✅ Cleaned data successfully saved to {PROCESSED_FILE}")

    profile_dataset(df_cleaned, "Processed")


if __name__ == "__main__":
    main()
