#!/usr/bin/env python3
"""Step 3 of the pipeline: build the analysis-ready table (cleaned -> analysis-ready).

Run from the repository root (after scripts/transform.py):
    python scripts/advanced_transform.py

Input : data/processed/dpwh_flood_control_projects_cleaned.csv
Output: data/processed/dpwh_flood_control_analysis_ready.csv

What this step does:
1. Makes one row per project_id. Multi-year contracts (MYCA) appear once per
   funding year, and only the first funding year's row carries the cost; later
   rows only say "MYCA with Project ID ...". So for each project:
   - the cost is the sum of its numeric costs (the MYCA rows add nothing), and
   - the descriptive fields come from the row that carries the cost.
   This does not depend on the order of rows in the file.
2. Fills the four grouping text columns with "Unknown" if they are empty.
3. Compares each project's cost with the average cost in its region
   (regional mean, standard deviation, difference and z-score).
4. Flags a project as a high-cost outlier when its z-score is 2.0 or more,
   meaning its cost is at least two standard deviations above its region's mean.

Earlier versions kept the first row of each project and filled a missing cost
with 0. Because the first row of 27 MYCA projects is a continuation row, those
projects got a cost of 0 (total PHP 543.7B instead of 545.6B, 329 outliers
instead of 326). Every correct way of deduplicating gives the numbers produced now.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

INPUT_FILE = Path("data/processed/dpwh_flood_control_projects_cleaned.csv")
OUTPUT_FILE = Path("data/processed/dpwh_flood_control_analysis_ready.csv")
COST = "contract_cost_php"
OUTLIER_Z = 2.0
TEXT_GROUP_COLUMNS = ["district_engineering_office", "contractor", "province", "region"]


def build_analysis_ready(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # 1. One row per project (see the docstring for why)
    before = len(out)
    project_cost = out.groupby("project_id")[COST].sum(min_count=1)   # NaN only if no row has a cost
    source_rows = out.groupby("project_id").size()
    has_cost = out[COST].notna()
    out = (out.assign(_has_cost=has_cost)
              .sort_values(["project_id", "_has_cost"], ascending=[True, False], kind="mergesort")
              .drop_duplicates(subset=["project_id"], keep="first")
              .drop(columns="_has_cost")
              .sort_index())                                            # back to source order
    out[COST] = out["project_id"].map(project_cost)
    out["source_rows"] = out["project_id"].map(source_rows)
    multi = (out["source_rows"] > 1).sum()
    print(f"Merged {before - len(out):,} repeated rows; {len(out):,} projects remain "
          f"({multi} multi-year projects now carry their real cost).")

    # 2. Grouping columns must not be empty
    for col in TEXT_GROUP_COLUMNS:
        out[col] = out[col].fillna("Unknown")

    # 3. Regional benchmark
    stats = out.groupby("region")[COST].agg(regional_avg_cost="mean", regional_std_cost="std")
    out = out.merge(stats, on="region", how="left")
    # A region with one project (or identical costs) has no spread; use 1 to avoid dividing by 0
    out["regional_std_cost"] = out["regional_std_cost"].replace(0, np.nan).fillna(1.0)
    out["cost_diff_from_regional_avg"] = (out[COST] - out["regional_avg_cost"]).round(2)
    out["cost_zscore_regional"] = (
        (out[COST] - out["regional_avg_cost"]) / out["regional_std_cost"]
    ).round(4)

    # 4. High-cost outlier flag
    out["is_high_cost_outlier"] = (out["cost_zscore_regional"] >= OUTLIER_Z).astype(int)

    # Round the benchmark columns so the file does not change with tiny
    # floating-point differences between pandas/numpy versions.
    out["regional_avg_cost"] = out["regional_avg_cost"].round(2)
    out["regional_std_cost"] = out["regional_std_cost"].round(2)
    return out


def validate(out: pd.DataFrame) -> None:
    problems = []
    if out["project_id"].duplicated().any():
        problems.append("project_id is not unique")
    if out[COST].isna().any() or (out[COST] <= 0).any():
        problems.append(f"{COST} has missing, zero or negative values")
    if out[TEXT_GROUP_COLUMNS].isna().any().any():
        problems.append("a grouping column has empty values")
    if not set(out["is_high_cost_outlier"].unique()) <= {0, 1}:
        problems.append("is_high_cost_outlier is not 0/1")
    if problems:
        sys.exit("Validation failed:\n  - " + "\n  - ".join(problems))
    rate = out["is_high_cost_outlier"].mean()
    print(f"Validation passed. {out['is_high_cost_outlier'].sum()} high-cost outliers ({rate:.1%}).")


def main() -> None:
    if not INPUT_FILE.exists():
        sys.exit(f"{INPUT_FILE} not found. Run scripts/transform.py first.")
    cleaned = pd.read_csv(INPUT_FILE)
    analysis_ready = build_analysis_ready(cleaned)
    validate(analysis_ready)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    analysis_ready.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
