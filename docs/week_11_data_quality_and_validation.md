# Week 11 — Data Quality, Validation & Reproducibility

**Project Title:** Public Data Patterns in DPWH Flood Control Projects (2022–2025)
**Target Audience:** Commission on Audit (COA) — Infrastructure Audit Division
**Scripts:** `scripts/transform.py`, `scripts/advanced_transform.py`
**Full cleaning log:** [`scripts/README.md`](../scripts/README.md)

---

## Summary

Both transform scripts check their output before saving it. If any check fails, the script stops with a message listing every problem, so a bad file is never written and the pipeline (`scripts/run_pipeline.py`) halts at that step.

---

## Validation checks

### `transform.py` (raw to cleaned)

| Check | Why |
|---|---|
| Row count equals the raw file (9,855) | Cleaning must not silently lose or add records |
| Required columns present | Later steps depend on them |
| No exact duplicate rows | Duplicates would double-count money |
| No missing `project_id` | Every record must be identifiable |
| (`project_id`, `contractid`, `fundingyear`) is unique | This is the true grain of the raw file |
| Both date columns are real dates with no invalid values | Time analysis needs valid dates |
| No start date after its completion date | Catches swapped or wrong dates |
| Money columns are numeric and non-negative | Sums and averages must be valid |

### `advanced_transform.py` (cleaned to analysis-ready)

| Check | Why |
|---|---|
| `project_id` is unique | One row per project |
| Every contract cost is present and non-negative | The z-score needs a number for every project |
| Grouping columns have no empty values | Region and province groupings must be complete |
| `is_high_cost_outlier` is only 0 or 1 | The flag must be a clean yes/no |

---

## Data quality decisions

| Issue | Decision | Reason |
| :--- | :--- | :--- |
| Text in money columns (28 costs, 157 budgets) | Set to empty in the cleaned file; original text kept in note columns | Keeps the columns numeric without losing information |
| Missing municipality (666 rows) | Left empty | Guessing would be wrong; no analysis groups by municipality |
| Repeated project IDs (28 rows) | Kept in the cleaned file; first row kept in the analysis-ready file | One row per project for counting and benchmarks |
| Empty cost after deduplication (27 projects) | Set to 0 (known limitation, see Week 10) | Every project needs a cost for the z-score |
| Coordinates | Checked once: all within the Philippines (lat 4 to 21, lon 116 to 127) | No flag needed |

---

## Reproducibility

- The same raw file always gives the same output files: there are no random steps, and the source row order is kept.
- The regional benchmark columns are rounded, so small floating-point differences between pandas and numpy versions do not change the files.
- Checked by running `python scripts/run_pipeline.py` twice and comparing every output file: all identical.
