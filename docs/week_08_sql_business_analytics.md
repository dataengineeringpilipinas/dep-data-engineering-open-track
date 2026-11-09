# Week 8 — SQL Business Analytics & Audit Queries

**Project Title:** Public Data Patterns in DPWH Flood Control Projects (2022–2025)
**Target Audience:** Commission on Audit (COA) — Infrastructure Audit Division
**Queries:** [`sql/business_questions.sql`](../sql/business_questions.sql)
**Runner:** `python scripts/run_sql_queries.py`

---

## Summary

Three SQL queries answer audit questions about contractor concentration, provincial funding and District Engineering Office (DEO) cost levels. `scripts/run_sql_queries.py` loads the cleaned file (`data/processed/dpwh_flood_control_projects_cleaned.csv`) into an in-memory SQLite table called `projects_cleaned`, runs each query in the `.sql` file and prints the answers.

The queries run on the cleaned table, not the raw file, because in the raw file the cost column is text (some rows say "MYCA with Project ID ..."), so sums and averages would be wrong.

---

## Business questions

1. **Contractor concentration:** Which 10 contractors received the largest total contract value?
2. **Geographic hotspots:** Which 15 provinces received the most flood control funding, and how many projects did each have?
3. **DEO cost levels:** Which District Engineering Offices (with at least 10 projects) have the highest average contract cost?

## How the queries handle the data

- `COUNT(DISTINCT project_id)` counts each project once. Multi-year contracts appear on more than one row in the cleaned table.
- Rows without a numeric cost (multi-year continuation rows) are empty in `contract_cost_php`, so `SUM` and `AVG` skip them.
- Column names are the cleaned names: `contractor`, `province`, `region`, `district_engineering_office`, `contract_cost_php`, `project_id`.

## Results (top rows)

| Question | Top result |
|---|---|
| 1 | Legacy Construction Corporation: 114 projects, about PHP 8.27B |
| 2 | Metro Manila: 1,057 projects, about PHP 52.6B; then Bulacan (668, PHP 43.8B) and Cebu (414, PHP 26.7B) |
| 3 | Butuan City DEO: average about PHP 131.3M across 48 projects |

These are totals, not adjusted for population or flood exposure. A large total is a place to look, not evidence of a problem.

## How to run

```bash
python scripts/transform.py        # if the cleaned file does not exist yet
python scripts/run_sql_queries.py
```
