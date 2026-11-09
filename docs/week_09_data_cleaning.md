# Week 9 — Data Cleaning & Shaping Deliverable

**Project Title:** Public Data Patterns in DPWH Flood Control Projects (2022–2025)
**Input:** `data/raw/dpwh_flood_control_projects.csv` (9,855 rows, 22 columns)
**Output:** `data/processed/dpwh_flood_control_projects_cleaned.csv` (9,855 rows, 24 columns)
**Script:** `scripts/transform.py`
**Full cleaning log:** [`scripts/README.md`](../scripts/README.md)

---

## Profiling findings and decisions

Inspecting the raw file with `df.info()` and `df.isna().sum()` showed:

1. **Mixed-case column names** (`ProjectId`, `ContractCost`, `DistrictEngineeringOffice`). All names are lowercased, and three are renamed to `project_id`, `contract_cost_php` and `district_engineering_office`.
2. **Text in money columns.** 28 `ContractCost` values and 157 `ApprovedBudgetForContract` values are text such as "MYCA with Project ID X" or "Clustered with Contract ID X". These become empty (NaN) so the columns can be numeric, and the original text is kept in `contract_cost_note` and `approved_budget_note`.
3. **Dates stored as text.** `actualcompletiondate` and `startdate` are converted to real dates. All 9,855 parse correctly.
4. **666 missing municipalities.** Left empty. Guessing a municipality would be wrong.
5. **No exact duplicate rows and no extra spaces in text columns.** Whitespace is still stripped as a safeguard.

This step keeps every row. Repeated project IDs (28 rows from multi-year contracts) are handled in Week 10.

---

## Column changes

| Raw column | Cleaned column | Type | Change |
| :--- | :--- | :--- | :--- |
| `ProjectId` | `project_id` | text | renamed |
| `DistrictEngineeringOffice` | `district_engineering_office` | text | renamed |
| `ContractCost` | `contract_cost_php` | number | renamed; text values become empty and move to `contract_cost_note` |
| `ApprovedBudgetForContract` | `approvedbudgetforcontract` | number | text values become empty and move to `approved_budget_note` |
| `ActualCompletionDate`, `StartDate` | `actualcompletiondate`, `startdate` | date | parsed as `YYYY-MM-DD` |
| all other columns | lowercase name | unchanged | whitespace stripped from text |

---

## How to run and verify

```bash
python scripts/transform.py
```

The script prints a profile before and after cleaning and stops with a message if any validation check fails (see Week 11).
