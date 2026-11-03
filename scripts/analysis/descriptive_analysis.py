import numpy as np
import pandas as pd
from pathlib import Path

# Safely locate and load the processed dataset
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "dep-data-engineering-open-track/data/processed/dpwh_flood_control_analysis_ready.csv").exists())
csv_path = ROOT / "dep-data-engineering-open-track/data/processed/dpwh_flood_control_analysis_ready.csv"
df = pd.read_csv(csv_path)

# -------------------------------------------------------------------------
# 1. Financial Metric: Contract Cost (PHP)
# -------------------------------------------------------------------------
cost_series = df["contract_cost_php"]
cost_stats = {
    "Mean": cost_series.mean(),
    "Median (P50)": cost_series.median(),
    "Std Dev": cost_series.std(),
    "Variance": cost_series.var(),
    "Min": cost_series.min(),
    "P25": cost_series.quantile(0.25),
    "P75": cost_series.quantile(0.75),
    "Max": cost_series.max(),
    "IQR": cost_series.quantile(0.75) - cost_series.quantile(0.25),
    "Skewness": cost_series.skew(),
}

# -------------------------------------------------------------------------
# 2. Risk Metric: Regional Cost Z-Score
# -------------------------------------------------------------------------
z_series = df["cost_zscore_regional"].dropna()
z_stats = {
    "Mean": z_series.mean(),
    "Median (P50)": z_series.median(),
    "Std Dev": z_series.std(),
    "Min": z_series.min(),
    "P25": z_series.quantile(0.25),
    "P75": z_series.quantile(0.75),
    "Max": z_series.max(),
    "Skewness": z_series.skew(),
    "Outliers (Z > 3.0)": (z_series > 3.0).sum(),
}

# -------------------------------------------------------------------------
# 3. Categorical Metrics Summary
# -------------------------------------------------------------------------
projects_per_contractor = df["contractor"].value_counts()
projects_per_province = df["province"].value_counts()

# Print formatted summary tables
print("=== 1. FINANCIAL METRIC: contract_cost_php (in PHP) ===")
for k, v in cost_stats.items():
    if "Skewness" in k:
        print(f"  • {k:<18}: {v:.4f}")
    else:
        print(f"  • {k:<18}: ₱{v:,.2f}")

print("\n=== 2. STATISTICAL RISK METRIC: cost_zscore_regional ===")
for k, v in z_stats.items():
    if "Outliers" in k:
        print(f"  • {k:<18}: {v:,} projects")
    else:
        print(f"  • {k:<18}: {v:.4f}")

print("\n=== 3. CATEGORICAL CONCENTRATION SUMMARY ===")
print(
    f"  • Total Projects Analyzed   : {len(df):,} records"
)
print(
    f"  • Active Contractors        : {df['contractor'].nunique():,} unique entities"
)
print(
    f"  • Median Projects / Contractor: {projects_per_contractor.median():.0f} (Max: {projects_per_contractor.max():,})"
)
print(
    f"  • Provinces Covered         : {df['province'].nunique():,} unique provinces"
)