from pathlib import Path
import numpy as np
import pandas as pd
from IPython.display import display

# File Paths
RAW_FILE = Path("data/raw/dpwh_flood_control_projects.csv")
PROCESSED_FILE = Path("data/processed/dpwh_flood_control_analysis_ready.csv")


def profile_dataset(df: pd.DataFrame, stage: str = "Raw") -> None:
    """Prints diagnostic structural metrics and column datatypes."""
    print(f"\n=================== {stage} Data Profile ===================")
    print(f"Shape: {df.shape[0]:,} rows, {df.shape[1]} columns")
    print("\n--- Summary Info ---")
    df.info(memory_usage="deep")
    print("\n--- Missing Values Count ---")
    print(df.isnull().sum()[df.isnull().sum() > 0])
    print("\n--- Preview ---")
    display(df.head(3))
    print("============================================================\n")


def advanced_transform_dpwh(df: pd.DataFrame) -> pd.DataFrame:
    """Executes advanced data cleaning, type conversions, regional aggregations,

    and audit feature engineering for DPWH flood control data.
    """
    df_transformed = df.copy()

    # ------------------------------------------------------------------
    # 1. Schema Standardization & Renaming
    # ------------------------------------------------------------------
    df_transformed.columns = [
        col.strip().lower().replace(" ", "_") for col in df_transformed.columns
    ]

    rename_mapping = {
        "projectid": "project_id",
        "districtengineeringoffice": "district_engineering_office",
        "contractcost": "contract_cost_php",
        "contractor": "contractor",
        "province": "province",
        "region": "region",
        "completiondate": "completion_date",
        "latitude": "latitude",
        "longitude": "longitude",
    }
    df_transformed.rename(columns=rename_mapping, inplace=True)

    # ------------------------------------------------------------------
    # 2. Duplicate Removal & Text Sanitation
    # ------------------------------------------------------------------
    initial_count = len(df_transformed)
    df_transformed.drop_duplicates(subset=["project_id"], keep="first", inplace=True)
    deduped_count = initial_count - len(df_transformed)
    if deduped_count > 0:
        print(f"🧹 Dropped {deduped_count:,} duplicate project entries.")

    string_cols = ["district_engineering_office", "contractor", "province", "region"]
    for col in string_cols:
        if col in df_transformed.columns:
            df_transformed[col] = df_transformed[col].astype(str).str.strip()
            df_transformed[col] = df_transformed[col].replace(
                ["nan", "None", "", "N/A", "null"], "Unknown"
            )

    # ------------------------------------------------------------------
    # 3. Type Conversion: Financial & Dates
    # ------------------------------------------------------------------
    # Financial Numeric Parsing
    df_transformed["contract_cost_php"] = pd.to_numeric(
        df_transformed["contract_cost_php"], errors="coerce"
    ).fillna(0.0)

    # Date Conversions & Extracting Time-Based Features
    if "completion_date" in df_transformed.columns:
        df_transformed["completion_date"] = pd.to_datetime(
            df_transformed["completion_date"], errors="coerce"
        )
        df_transformed["completion_year"] = df_transformed["completion_date"].dt.year.fillna(-1).astype(int)
        df_transformed["completion_quarter"] = df_transformed["completion_date"].dt.quarter.fillna(-1).astype(int)
        df_transformed["completion_month"] = df_transformed["completion_date"].dt.month.fillna(-1).astype(int)

    # Coordinates Parsing
    for coord_col in ["latitude", "longitude"]:
        if coord_col in df_transformed.columns:
            df_transformed[coord_col] = pd.to_numeric(df_transformed[coord_col], errors="coerce")

    # ------------------------------------------------------------------
    # 4. Regional Aggregations & Cost Z-Score Engineering
    # ------------------------------------------------------------------
    print("📊 Computing regional cost benchmarks and statistical Z-scores...")

    # Calculate regional mean and standard deviation for contract cost
    regional_stats = (
        df_transformed.groupby("region")["contract_cost_php"]
        .agg(regional_avg_cost="mean", regional_std_cost="std")
        .reset_index()
    )

    # Merge regional stats back into main dataset
    df_transformed = df_transformed.merge(regional_stats, on="region", how="left")

    # Handle standard deviation zero/NaN cases to prevent division by zero
    df_transformed["regional_std_cost"] = df_transformed["regional_std_cost"].replace(0, np.nan).fillna(1.0)

    # Feature 1: Deviation from Regional Average (in Pesos)
    df_transformed["cost_diff_from_regional_avg"] = (
        df_transformed["contract_cost_php"] - df_transformed["regional_avg_cost"]
    ).round(2)

    # Feature 2: Statistical Z-Score of Cost relative to Regional Mean
    df_transformed["cost_zscore_regional"] = (
        (df_transformed["contract_cost_php"] - df_transformed["regional_avg_cost"])
        / df_transformed["regional_std_cost"]
    ).round(4)

    # ------------------------------------------------------------------
    # 5. Risk Flag Engineering (COA Audit Indicators)
    # ------------------------------------------------------------------
    # Flag high-value project outliers (Cost Z-Score >= 2.0 standard deviations above regional mean)
    df_transformed["is_high_cost_outlier"] = (df_transformed["cost_zscore_regional"] >= 2.0).astype(int)

    # Flag coordinate completeness for audit site inspection
    if "latitude" in df_transformed.columns and "longitude" in df_transformed.columns:
        df_transformed["has_valid_coords"] = (
            df_transformed["latitude"].notnull() & df_transformed["longitude"].notnull()
        ).astype(int)

    return df_transformed


def main():
    if not RAW_FILE.exists():
        print(f"❌ Error: Raw dataset not found at {RAW_FILE.resolve()}")
        print("💡 Tip: Verify git clone and repository working directory in Colab!")
        return

    print(f"📥 Loading raw dataset from {RAW_FILE}...")
    df_raw = pd.read_csv(RAW_FILE)

    # 1. Profile raw inputs
    profile_dataset(df_raw, stage="Raw")

    # 2. Execute advanced cleaning & feature engineering
    print("⚙️ Executing advanced transformations, merges, and audit feature creation...")
    df_analysis_ready = advanced_transform_dpwh(df_raw)

    # 3. Profile analysis-ready output
    profile_dataset(df_analysis_ready, stage="Analysis-Ready")

    # 4. Export analysis-ready file
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    df_analysis_ready.to_csv(PROCESSED_FILE, index=False)
    print(f"✅ Success! Analysis-ready dataset exported to {PROCESSED_FILE}")


# Direct execution inside Google Colab cell
main()