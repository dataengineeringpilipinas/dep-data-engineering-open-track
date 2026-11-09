# SQL folder

This folder contains SQL assets for the project’s data-processing and analysis layer.

## Files

- `schema_ddl.sql` — DDL for the analytical schema
- `business_questions.sql` — 3 business questions with SQL answers for contractor, province, and office analysis

## M3 alignment

These SQL assets support the DEP Milestone 3 requirements:
- schema plan documented
- at least 3 business questions answered in SQL
- processed and analytics-ready data structure outlined for downstream analysis

## How to run

```bash
python scripts/transform.py        # if data/processed/ is empty
python scripts/run_sql_queries.py  # prints the answers to all three questions
```

The queries run on the cleaned table (`data/processed/dpwh_flood_control_projects_cleaned.csv`), loaded into an in-memory SQLite table called `projects_cleaned`.

`schema_ddl.sql` is the planned star schema from Week 7. The implemented pipeline uses CSV files and does not build these tables yet.
