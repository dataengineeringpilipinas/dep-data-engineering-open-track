# Scripts

Run everything from the repository root. `python scripts/run_pipeline.py` runs steps 2 to 5 in order.

| Step | Script | Input | Output |
|---|---|---|---|
| 1 | `ingest.py` | Kaggle API (needs credentials) | `data/raw/dpwh_flood_control_projects.csv`, `data/raw/SOURCE.md` |
| 2 | `transform.py` | raw CSV | `data/processed/dpwh_flood_control_projects_cleaned.csv` |
| 3 | `advanced_transform.py` | cleaned CSV | `data/processed/dpwh_flood_control_analysis_ready.csv` |
| 4 | `analysis/m5_segmentation_kpis.py` | analysis-ready CSV | `data/processed/m5_*.csv`, `output/figures/m5_*.png` |
| 5 | `build_dashboard.py` | analysis-ready + `m5_*.csv` | `dashboard/index.html` |

Other tools:

- `run_sql_queries.py` runs the three Week 8 questions in `sql/business_questions.sql` on the cleaned CSV and prints the answers.
- `check_links.py` is the final QA check: README and docs links resolve, required files exist, the live URL is in the README.

## Cleaning log: raw to cleaned (`transform.py`)

**Input:** 9,855 rows, 22 columns. **Output:** 9,855 rows, 24 columns (22 + 2 note columns).
**Principle:** no rows are dropped and no values are invented. A value that is not a real number becomes empty (NaN), and the original text is kept in a note column.

| # | Issue | Rows | Decision | Reason |
|---|---|---|---|---|
| 1 | Column names in mixed case | all | Lowercase; rename to `project_id`, `district_engineering_office`, `contract_cost_php` | One consistent naming style for every later step |
| 2 | `Municipality` blank | 666 | Keep empty | These are real projects; filling in a guess would be wrong |
| 3 | `ContractCost` is the text "MYCA with Project ID X" | 28 | Set cost to empty; keep the text in `contract_cost_note` | Multi-year contract (MYCA): the money is recorded on another funding-year row of the same project |
| 4 | `ApprovedBudgetForContract` is text: "Clustered with Contract ID X" (129) or "MYCA with Project ID X" (28) | 157 | Set budget to empty; keep the text in `approved_budget_note` | The budget is bundled under another contract, not zero. Empty, not 0, so totals are not understated |
| 5 | Dates stored as text | all | Convert `actualcompletiondate` and `startdate` to dates | Dates must be dates for time-based analysis |
| 6 | Repeated `project_id` | 28 | No change in this step | Expected MYCA pattern. The true grain of the raw file is (`project_id`, `contractid`, `fundingyear`) |

Checked, no action needed: 0 exact duplicate rows, no extra spaces in text columns, 0 projects that start after completion, 0 coordinates outside the Philippines (lat 4 to 21, lon 116 to 127).

Kept as-is for analysis: 769 rows where the contract cost is above the approved budget (KPI 5), and project durations from 14 to 2,012 days.

**Validation checks** (the script stops if any fails): row count equals raw; required columns present; no exact duplicates; no missing `project_id`; (`project_id`, `contractid`, `fundingyear`) unique; dates are valid and start is not after completion; money columns numeric and non-negative.

## Cleaned to analysis-ready (`advanced_transform.py`)

**Output:** 9,827 rows (one per project), 29 columns.

1. Keep the first row for each `project_id` (drops 28 rows).
2. Fill empty `region`, `province`, `contractor`, `district_engineering_office` with "Unknown" (none are empty today).
3. Set an empty contract cost to 0.
4. Add `regional_avg_cost`, `regional_std_cost`, `cost_diff_from_regional_avg` and `cost_zscore_regional`.
5. Add `is_high_cost_outlier` = 1 when `cost_zscore_regional` is 2.0 or more (329 projects, 3.3%).

**Known limitation of steps 1 and 3.** For 27 MYCA projects the first row is a continuation row with no cost, so the project ends up with cost 0 and its real cost is dropped. These rows are marked in `contract_cost_note`. Keeping the row that has the cost instead would raise total value from PHP 543.7B to PHP 545.6B and change the outlier count from 329 to 326; the regional ranking (Region IV-B highest) does not change. The published results still use the current rule.

## Reproducibility

The same raw file gives the same output files on every run: no random steps, source row order is kept, and the regional benchmark columns are rounded so tiny floating-point differences between library versions do not change the files.
