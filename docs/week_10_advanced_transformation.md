# Week 10 — Advanced Transformation & Feature Engineering

**Project Title:** Public Data Patterns in DPWH Flood Control Projects (2022–2025)
**Input:** `data/processed/dpwh_flood_control_projects_cleaned.csv` (output of Week 9)
**Output:** `data/processed/dpwh_flood_control_analysis_ready.csv` (9,827 rows, 29 columns)
**Script:** `scripts/advanced_transform.py`

---

## Overview

Week 10 turns the cleaned table into an analysis-ready table with one row per project, a regional cost benchmark and an audit flag for unusually costly projects.

---

## Steps

### 1. One row per project
`drop_duplicates(subset=["project_id"], keep="first")` removes 28 repeated rows from multi-year contracts, leaving 9,827 projects.

### 2. Missing values
- **Grouping text** (`contractor`, `province`, `region`, `district_engineering_office`): empty values would become `"Unknown"`. None are empty today.
- **Contract cost:** an empty cost is set to `0.0` so every project has a number.

**Known limitation.** For 27 multi-year projects, the row kept in step 1 is a continuation row with no cost, so these projects get cost 0. They are marked in `contract_cost_note`. Keeping the row that has the cost would change the total from PHP 543.7B to PHP 545.6B and the outlier count from 329 to 326. See [`scripts/README.md`](../scripts/README.md).

### 3. Regional benchmark (`groupby` + `merge`)
For each region, the script computes the mean and standard deviation of contract cost and joins them back to every project:

$$\text{z-score} = \frac{\text{contract cost} - \text{regional mean}}{\text{regional standard deviation}}$$

### 4. Features added

| Column | Type | Logic | Why |
| :--- | :--- | :--- | :--- |
| `regional_avg_cost` | number | mean cost in the project's region | benchmark |
| `regional_std_cost` | number | standard deviation of cost in the region (1 if the region has no spread) | benchmark |
| `cost_diff_from_regional_avg` | number | `contract_cost_php - regional_avg_cost` | peso difference from the regional norm |
| `cost_zscore_regional` | number | the z-score above | compares projects across regions with different cost levels |
| `is_high_cost_outlier` | 0/1 | 1 if `cost_zscore_regional >= 2.0` | 329 projects (3.3%) to look at first |

Time features are not added here. Completion year and quarter, and the time-adjusted outlier flag (z-score within region **and** completion year), are computed in Phase 5 by `scripts/analysis/m5_segmentation_kpis.py`, because costs rose over time and the plain regional flag over-flags recent projects.

---

## How to run

```bash
python scripts/advanced_transform.py   # after scripts/transform.py
```

Or run the whole pipeline with `python scripts/run_pipeline.py`.
