Week 9 — Data Cleaning & Shaping Deliverable

**Project Title:** Public Data Patterns in DPWH Flood Control Projects (2022–2025)  
**Input:** `data/raw/dpwh_flood_control_projects.csv`  
**Output:** `data/processed/dpwh_flood_control_projects_cleaned.csv`  

---

## Executive Summary & Profiling Decisions

During initial data inspection via `df.info()` and `df.isnull().sum()`, key data quality baseline items were identified and addressed:

1. **Schema Standardization:** Column names like `DistrictEngineeringOffice`, `ProjectId`, and `ContractCost` were converted to standard lower `snake_case` (`district_engineering_office`, `project_id`, `contract_cost_php`).
2. **Text Normalization:** String columns (`contractor`, `province`, `region`, `district_engineering_office`) contained whitespace inconsistencies and null variants (`nan`, `N/A`), which were trimmed and normalized to `'Unknown'`.
3. **Numeric Type Enforcement:** `contract_cost_php` was coerced to `float64` to prevent financial aggregation errors during downstream SQL/Pandas analysis.
4. **Deduplication:** Dropped exact duplicated project records across all attributes.

---

## Data Cleaning Pipeline (`scripts/transform.py`)

| Raw Field Name | Processed Field Name | Target Data Type | Transformation Applied |
| :--- | :--- | :--- | :--- |
| `ProjectId` | `project_id` | `String` | Strip whitespace, convert to snake_case |
| `DistrictEngineeringOffice` | `district_engineering_office` | `String` | Clean text, fill empty values with `'Unknown'` |
| `ContractCost` | `contract_cost_php` | `Float64` | Parse numeric currency, fill invalid/null with `0.0` |
| `Contractor` | `contractor` | `String` | Strip leading/trailing spaces, standardize text |
| `Province` | `province` | `String` | Trim string padding, map empty values to `'Unknown'` |
| `Region` | `region` | `String` | Standardize administrative region names |

---

## 🔄 How to Run and Verify

To execute the data cleaning pipeline locally:

```bash
python scripts/transform.py
