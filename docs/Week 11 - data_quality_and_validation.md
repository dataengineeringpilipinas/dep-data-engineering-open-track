# Week 11 — Data Quality, Validation & Reproducibility

**Project Title:** Public Data Patterns in DPWH Flood Control Projects (2022–2025)  
**Target Audience:** Commission on Audit (COA) — Infrastructure Audit Division  
**Document Path:** `docs/data_quality_and_validation.md`  

---

##  Executive Summary

Week 11 establishes an automated data quality validation layer within the transformation pipeline (`scripts/advanced_transform.py`). By introducing lightweight, deterministic assertion checks, boundary validations, and an explicit cleaning log, this milestone guarantees that running the transformation script against the raw dataset consistently yields identical, audit-ready outputs across both Google Colab and local Python runtime environments.

---

## 🛠️ Step 1: Validated Transformation Pipeline Summary

The transformation script enforces data quality through a multi-stage validation flow:

1. **Schema Standardization:** Strips leading/trailing spaces and converts raw column headers to standard `snake_case`.
2. **Deduplication:** Filters duplicate records based on `project_id` while maintaining execution logging.
3. **Missingness Imputation:** Imputes blank or missing string values with `'Unknown'` to preserve financial aggregates without dropping valid project records.
4. **Type Coercion & Bounds Verification:** Converts string values to numeric floats, coercing invalid strings to numeric defaults and flagging out-of-bounds geographic coordinates.
5. **Assertion Execution:** Executes strict `assert` statements before saving processed outputs to disk.

---

##  Step 2: Data Quality & Cleaning Decision Log

| Quality Issue / Risk | Cleaning Strategy Applied | Decision Rationale |
| :--- | :--- | :--- |
| **Missing Categoricals** | Replaced nulls (`nan`, `None`, `""`) with `'Unknown'` in `contractor`, `province`, `region`, and `district_engineering_office`. | Retains project cost records for aggregate national allocations without dropping valid contract entries. |
| **Duplicate Project Entries** | Executed `df.drop_duplicates(subset=["project_id"], keep="first")`. | Prevents artificial inflation of contract allocations and total project counts during regional aggregations. |
| **Numeric/Currency Parsing** | Coerced `contract_cost_php` strings to float values using `pd.to_numeric(..., errors='coerce')` and filled NaNs with `0.0`. | Ensures mathematical stability during regional $Z$-score calculations and avoids runtime execution exceptions. |
| **Unparsed Date Formats** | Parsed `completion_date` strings into `datetime64[ns]` and extracted temporal breakdown features (`completion_year`, `completion_quarter`, `completion_month`). | Enables time-series analysis while isolating unparseable date strings into default missing indicators (`-1`). |
| **Out-of-Bounds Coordinates** | Computed binary indicator `has_valid_coords` based on Philippine territorial GPS bounds ($4.0^\circ \text{N} \le \text{Lat} \le 22.0^\circ \text{N}$, $116.0^\circ \text{E} \le \text{Lon} \le 127.0^\circ \text{E}$). | Flags invalid GPS entries for spatial audit sampling without discarding contract cost records from financial analysis. |

---

##  Step 3: Programmatic Assertion Checks

The pipeline enforces five automated assertion checks in code prior to writing output files:

```python
def run_validation_checks(df: pd.DataFrame) -> None:
    """Executes programmatic data quality assertions on transformed dataframe."""
    print(" Running automated data quality assertion checks...")

    # Rule 1: Primary key completeness
    assert df["project_id"].isna().sum() == 0, \
        " Validation Error: Primary key 'project_id' contains null values."

    # Rule 2: Primary key uniqueness
    assert df["project_id"].nunique() == len(df), \
        f" Validation Error: 'project_id' is not unique ({df['project_id'].nunique():,} unique vs {len(df):,} rows)."

    # Rule 3: Non-negative financial contract amounts
    assert (df["contract_cost_php"] >= 0).all(), \
        " Validation Error: Negative contract costs detected in 'contract_cost_php'."

    # Rule 4: Critical categorical missingness boundary (< 5% unknown region rate)
    unknown_region_rate = (df["region"] == "Unknown").sum() / len(df)
    assert unknown_region_rate <= 0.05, \
        f" Validation Error: 'region' field missingness exceeds 5% limit ({unknown_region_rate:.2%})."

    # Rule 5: Derived audit risk flags binary boundary
    if "is_high_cost_outlier" in df.columns:
        assert set(df["is_high_cost_outlier"].unique()).issubset({0, 1}), \
            " Validation Error: 'is_high_cost_outlier' contains non-binary values."

    print("✅ All validation checks passed successfully!")
