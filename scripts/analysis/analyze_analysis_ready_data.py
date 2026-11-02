from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    ROOT = Path(__file__).resolve().parents[2]
except NameError:
    ROOT = Path.cwd()

DEFAULT_INPUT = ROOT / "data" / "processed" / "dpwh_flood_control_analysis_ready.csv"
DEFAULT_OUTPUT = ROOT / "data" / "output" / "analysis"

# Updated to match the actual CSV lowercase column headers
REQUIRED_COLUMNS = {
    "region",
    "province",
    "project_id",
    "fundingyear",
    "approvedbudgetforcontract",
    "contract_cost_php",
    "contractor",
}


def summarize_geography(df: pd.DataFrame, column: str) -> pd.DataFrame:
    grouped = df.assign(_group=df[column].fillna("Unknown")).groupby("_group", dropna=False)
    summary = grouped.agg(
        project_rows=("project_id", "size"),
        unique_projects=("project_id", "nunique"),
        approved_budget_total=("approvedbudgetforcontract", "sum"),
        contract_cost_total=("contract_cost_php", "sum"),
        average_contract_cost=("contract_cost_php", "mean"),
    )
    summary.index.name = column
    return summary.reset_index().sort_values("contract_cost_total", ascending=False)


def contractor_summary(df: pd.DataFrame) -> pd.DataFrame:
    awards = df[["project_id", "contractor"]].copy()
    awards["contractor"] = awards["contractor"].fillna("").str.split("/")
    awards = awards.explode("contractor")
    awards["contractor"] = awards["contractor"].str.strip()
    awards = awards.loc[awards["contractor"].ne("")]
    summary = awards.groupby("contractor").agg(
        award_rows=("project_id", "size"),
        unique_projects=("project_id", "nunique"),
    )
    summary["award_share"] = summary["award_rows"] / summary["award_rows"].sum()
    summary.index.name = "Contractor"
    return summary.reset_index().sort_values("award_rows", ascending=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze geographic, financial, and contractor patterns in the cleaned DPWH data."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Cleaned dataset path")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Directory for analysis outputs")
    args, unknown = parser.parse_known_args() 

    if not args.input.is_file():
        colab_fallback = Path("/content/data/processed/dpwh_flood_control_analysis_ready.csv")
        if colab_fallback.is_file():
            args.input = colab_fallback
        else:
            parser.error(f"input file not found: {args.input}")

    df = pd.read_csv(args.input)
    missing_columns = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing_columns:
        parser.error(f"input is missing required columns: {', '.join(missing_columns)}")

    for column in ("approvedbudgetforcontract", "contract_cost_php", "fundingyear"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summarize_geography(df, "region").to_csv(args.output_dir / "projects_by_region.csv", index=False)
    summarize_geography(df, "province").to_csv(args.output_dir / "projects_by_province.csv", index=False)
    contractor_summary(df).to_csv(args.output_dir / "projects_by_contractor.csv", index=False)

    yearly = df.groupby("fundingyear", dropna=False).agg(
        project_rows=("project_id", "size"),
        unique_projects=("project_id", "nunique"),
        approved_budget_total=("approvedbudgetforcontract", "sum"),
        contract_cost_total=("contract_cost_php", "sum"),
        average_contract_cost=("contract_cost_php", "mean"),
    )
    yearly.reset_index().to_csv(args.output_dir / "projects_by_funding_year.csv", index=False)

    valid_costs = df["contract_cost_php"].dropna()
    if valid_costs.empty:
        lower_fence = upper_fence = float("nan")
    else:
        q1, q3 = valid_costs.quantile([0.25, 0.75])
        spread = q3 - q1
        lower_fence = q1 - 1.5 * spread
        upper_fence = q3 + 1.5 * spread

    over_budget = (
        df["contract_cost_php"].notna()
        & df["approvedbudgetforcontract"].notna()
        & df["contract_cost_php"].gt(df["approvedbudgetforcontract"])
    )
    cost_outlier = df["contract_cost_php"].notna() & (
        df["contract_cost_php"].lt(lower_fence) | df["contract_cost_php"].gt(upper_fence)
    )
    review = df.loc[
        over_budget | cost_outlier,
        [
            column
            for column in (
                "project_id",
                "contractid",
                "region",
                "province",
                "municipality",
                "fundingyear",
                "approvedbudgetforcontract",
                "contract_cost_php",
                "contractor",
            )
            if column in df.columns
        ],
    ].copy()
    review["contract_cost_above_approved_budget"] = over_budget.loc[review.index]
    review["contract_cost_iqr_outlier"] = cost_outlier.loc[review.index]
    review.to_csv(args.output_dir / "projects_for_review.csv", index=False)

    years = df["fundingyear"].dropna()
    report = [
        "DPWH FLOOD CONTROL PROJECTS - CLEANED-DATA ANALYSIS",
        f"Input: {args.input}",
        f"Rows: {len(df):,}",
        f"Unique project IDs: {df['project_id'].nunique():,}",
        f"Regions: {df['region'].nunique():,}",
        f"Provinces: {df['province'].nunique():,}",
        f"Funding years: {int(years.min())} to {int(years.max())}" if not years.empty else "Funding years: unavailable",
        f"Approved budget total (known values): PHP {df['approvedbudgetforcontract'].sum():,.2f}",
        f"Contract cost total (known values): PHP {df['contract_cost_php'].sum():,.2f}",
        f"Rows with missing municipality: {int(df['municipality'].isna().sum()) if 'municipality' in df.columns else 'not available'}",
        f"Rows with contract cost above approved budget: {int(over_budget.sum())}",
        f"Rows with contract cost outside 1.5x IQR fences: {int(cost_outlier.sum())}",
        f"Rows flagged for review: {len(review)}",
        "",
        "Cost and concentration flags are screening indicators only; they do not establish wrongdoing.",
        "Grouped CSVs and project-level review flags are saved in the output directory.",
    ]
    report_text = "\n".join(report) + "\n"
    (args.output_dir / "analysis_summary.txt").write_text(report_text, encoding="utf-8")
    print(report_text, end="")
    print(f"Output directory: {args.output_dir}")


if __name__ == "__main__":
    main()
