from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "processed" / "dpwh_flood_control_projects_cleaned.csv"
DEFAULT_OUTPUT = ROOT / "data" / "output" / "analysis"

REQUIRED_COLUMNS = {
    "Region",
    "Province",
    "ProjectId",
    "FundingYear",
    "ApprovedBudgetForContract",
    "ContractCost",
    "Contractor",
}


def summarize_geography(df: pd.DataFrame, column: str) -> pd.DataFrame:
    grouped = df.assign(_group=df[column].fillna("Unknown")).groupby("_group", dropna=False)
    summary = grouped.agg(
        project_rows=("ProjectId", "size"),
        unique_projects=("ProjectId", "nunique"),
        approved_budget_total=("ApprovedBudgetForContract", "sum"),
        contract_cost_total=("ContractCost", "sum"),
        average_contract_cost=("ContractCost", "mean"),
    )
    summary.index.name = column
    return summary.reset_index().sort_values("contract_cost_total", ascending=False)


def contractor_summary(df: pd.DataFrame) -> pd.DataFrame:
    awards = df[["ProjectId", "Contractor"]].copy()
    awards["Contractor"] = awards["Contractor"].fillna("").str.split("/")
    awards = awards.explode("Contractor")
    awards["Contractor"] = awards["Contractor"].str.strip()
    awards = awards.loc[awards["Contractor"].ne("")]
    summary = awards.groupby("Contractor").agg(
        award_rows=("ProjectId", "size"),
        unique_projects=("ProjectId", "nunique"),
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
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input file not found: {args.input}")

    df = pd.read_csv(args.input)
    missing_columns = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing_columns:
        parser.error(f"input is missing required columns: {', '.join(missing_columns)}")

    for column in ("ApprovedBudgetForContract", "ContractCost", "FundingYear"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summarize_geography(df, "Region").to_csv(args.output_dir / "projects_by_region.csv", index=False)
    summarize_geography(df, "Province").to_csv(args.output_dir / "projects_by_province.csv", index=False)
    contractor_summary(df).to_csv(args.output_dir / "projects_by_contractor.csv", index=False)

    yearly = df.groupby("FundingYear", dropna=False).agg(
        project_rows=("ProjectId", "size"),
        unique_projects=("ProjectId", "nunique"),
        approved_budget_total=("ApprovedBudgetForContract", "sum"),
        contract_cost_total=("ContractCost", "sum"),
        average_contract_cost=("ContractCost", "mean"),
    )
    yearly.reset_index().to_csv(args.output_dir / "projects_by_funding_year.csv", index=False)

    valid_costs = df["ContractCost"].dropna()
    if valid_costs.empty:
        lower_fence = upper_fence = float("nan")
    else:
        q1, q3 = valid_costs.quantile([0.25, 0.75])
        spread = q3 - q1
        lower_fence = q1 - 1.5 * spread
        upper_fence = q3 + 1.5 * spread

    over_budget = (
        df["ContractCost"].notna()
        & df["ApprovedBudgetForContract"].notna()
        & df["ContractCost"].gt(df["ApprovedBudgetForContract"])
    )
    cost_outlier = df["ContractCost"].notna() & (
        df["ContractCost"].lt(lower_fence) | df["ContractCost"].gt(upper_fence)
    )
    review = df.loc[
        over_budget | cost_outlier,
        [
            column
            for column in (
                "ProjectId",
                "ContractId",
                "Region",
                "Province",
                "Municipality",
                "FundingYear",
                "ApprovedBudgetForContract",
                "ContractCost",
                "Contractor",
            )
            if column in df.columns
        ],
    ].copy()
    review["contract_cost_above_approved_budget"] = over_budget.loc[review.index]
    review["contract_cost_iqr_outlier"] = cost_outlier.loc[review.index]
    review.to_csv(args.output_dir / "projects_for_review.csv", index=False)

    years = df["FundingYear"].dropna()
    report = [
        "DPWH FLOOD CONTROL PROJECTS - CLEANED-DATA ANALYSIS",
        f"Input: {args.input}",
        f"Rows: {len(df):,}",
        f"Unique project IDs: {df['ProjectId'].nunique():,}",
        f"Regions: {df['Region'].nunique():,}",
        f"Provinces: {df['Province'].nunique():,}",
        f"Funding years: {int(years.min())} to {int(years.max())}" if not years.empty else "Funding years: unavailable",
        f"Approved budget total (known values): PHP {df['ApprovedBudgetForContract'].sum():,.2f}",
        f"Contract cost total (known values): PHP {df['ContractCost'].sum():,.2f}",
        f"Rows with missing municipality: {int(df['Municipality'].isna().sum()) if 'Municipality' in df.columns else 'not available'}",
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
