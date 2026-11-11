## Transformation Report: raw to analysis-ready

Written by hand from the output of `python scripts/run_pipeline.py` (Weeks 10 and 11). The detailed cleaning log is in [`scripts/README.md`](../scripts/README.md).

## Data volume

| | Raw | Cleaned | Analysis-ready |
| :--- | :--- | :--- | :--- |
| File | `data/raw/dpwh_flood_control_projects.csv` | `data/processed/dpwh_flood_control_projects_cleaned.csv` | `data/processed/dpwh_flood_control_analysis_ready.csv` |
| Rows | 9,855 | 9,855 | 9,827 (one per project) |
| Columns | 22 | 24 | 30 |
| Made by | `scripts/ingest.py` | `scripts/transform.py` | `scripts/advanced_transform.py` |

## Features added in the analysis-ready file

1. **`regional_avg_cost`**: average contract cost in the project's region.
2. **`regional_std_cost`**: standard deviation of contract cost in the region.
3. **`cost_diff_from_regional_avg`**: project cost minus the regional average (PHP).
4. **`cost_zscore_regional`**: how many standard deviations the cost is from the regional average.
5. **`is_high_cost_outlier`**: 1 when the z-score is 2.0 or more (326 projects, 3.3%).
6. **`source_rows`**: how many raw rows the project had (2 or 3 for the 27 multi-year projects, otherwise 1).

Two note columns carry over from the cleaned file: `contract_cost_note` and `approved_budget_note` keep the original text where a money value was not a number.

Time features (completion year and quarter) and the time-adjusted outlier flag are added later, in `scripts/analysis/m5_segmentation_kpis.py` (`prepare`).

## Validation checks that pass on every run

- [x] `project_id` has no missing values and is unique in the analysis-ready file
- [x] Contract costs are present and above zero
- [x] `is_high_cost_outlier` is only 0 or 1
- [x] Grouping columns (region, province, contractor, district office) have no empty values

## Multi-year (MYCA) projects

27 projects appear on more than one funding-year row, with the cost on only one of them. Each is kept once with its real cost. An earlier version recorded them at cost 0; see `scripts/README.md` for the correction and its effect.
