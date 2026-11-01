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
        "projectid": "project_id",
        "districtengineeringoffice": "district_engineering_office",
        "contractcost": "contract_cost_php",
        "contractor": "contractor",
        "province": "province",
        "region": "region",
    }
    df_clean.rename(columns=rename_mapping, inplace=True)

    # 2. Clean text columns (strip leading/trailing whitespace & handle missing text)
    string_cols = df_clean.select_dtypes(include=["object"]).columns
    for col in string_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip()
        # Normalize empty strings or stringified nulls to 'Unknown'
        df_clean[col] = df_clean[col].replace(["nan", "None", "", "N/A"], "Unknown")

    # 3. Clean numeric fields (ensure contract cost is valid float)
    if "contract_cost_php" in df_clean.columns:
        df_clean["contract_cost_php"] = pd.to_numeric(
            df_clean["contract_cost_php"], errors="coerce"
        ).fillna(0.0)

    # 4. Remove exact duplicate rows if any exist
    initial_rows = len(df_clean)
    df_clean.drop_duplicates(inplace=True)
    deduped_rows = initial_rows - len(df_clean)
    if deduped_rows > 0:
        print(f"\ud83e\uddf9 Removed {deduped_rows:,} exact duplicate rows.")

    return df_clean


def main():
    if not RAW_FILE.exists():
        print(f"Error: Raw data file not found at {RAW_FILE}")
        return

    # Load and Profile Raw Dataset
    df_raw = pd.read_csv(RAW_FILE)
    profile_dataset(df_raw, "Raw")

    # Clean and Transform
    df_cleaned = clean_dpwh_dataset(df_raw)

    # Ensure destination directory exists before saving
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    df_cleaned.to_csv(PROCESSED_FILE, index=False)
    print(f"\u2705 Cleaned data successfully saved to {PROCESSED_FILE}")

    # Profile Processed Dataset
    profile_dataset(df_cleaned, "Processed")


if __name__ == "__main__":
    main()
