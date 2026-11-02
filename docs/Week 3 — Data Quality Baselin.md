# Week 3 — Data Quality Baseline, Governance & Risk Assessment

**Project Title:** Public Data Patterns in DPWH Flood Control Projects (2022–2025)  
**Target Audience:** Commission on Audit (COA) — Infrastructure Audit Division  
**Document Path:** `docs/week03_data_quality_and_governance.md`  

---

## Executive Summary

This document details the data quality baseline framework, risk assessment, data governance guidelines, and ethical principles established during Week 3. Before executing full raw data ingestion (Phase 2), this policy defines expected quality dimensions, addresses critical audit disclaimers regarding self-reported government datasets, and sets validation guardrails to prevent corrupted or unverified records from entering downstream pipeline layers.

---

## Data Quality Dimensions Matrix

To ensure data integrity for audit screening, public DPWH flood control records are evaluated across five core data quality dimensions:

| Quality Dimension | Assessment Metric | Pipeline Enforcement Strategy | Target Threshold |
| :--- | :--- | :--- | :--- |
| **Completeness** | Null rate across key fields (`ContractCost`, `Contractor`, `Province`, `Region`) | Flag missing mandatory fields and impute categorical nulls as `'Unknown'` | $\ge 95\%$ completeness on financial & spatial fields |
| **Accuracy** | Spatial coordinate validity ($11.0^\circ \le \text{Latitude} \le 21.0^\circ$, $118.0^\circ \le \text{Longitude} \le 127.0^\circ$) | Filter or flag out-of-bounds GPS coordinates outside Philippine territorial boundaries | $100\%$ valid geographic coordinate bounds |
| **Consistency** | Standardized naming conventions across District Engineering Offices (DEOs) and contractors | String sanitation, whitespace trimming, and snake_case schema normalization | Zero leading/trailing whitespace variations |
| **Timeliness** | Completion date temporal alignment ($2022 \le \text{Completion Year} \le 2025$) | Parse date fields into ISO-8601 (`YYYY-MM-DD`); coerce unparseable formats to `NaT` | $100\%$ valid date range parsing |
| **Validity** | Positive non-zero contract values ($\text{ContractCost} > 0$) | Coerce non-numeric string values to numeric floats; isolate zero/negative values | $100\%$ positive numeric currency values |

---

## Ingestion Risk Assessment & Audit Limitations

Analyzing government infrastructure data requires strict acknowledgement of inherent dataset limitations and external validation context:

### 1. Self-Reported Data Vulnerabilities
The raw dataset consists of self-reported project logs submitted by DPWH regional and district engineering offices. Self-reported records may contain reporting delays, manual keying errors, or omissions of ongoing project modifications.

### 2. Context of Senate Inquiries & Site Non-Existence
Formal legislative reviews (e.g., Senate Blue Ribbon Committee inquiries) and internal government validations have highlighted historical vulnerabilities in infrastructure reporting:
- **Site Non-Existence ("Ghost Projects"):** Isolated validation sampling in late 2025 flagged non-existent or misreported project locations (e.g., 15 out of ~1,600 validated sites confirmed non-existent, with ~160 pending field verification).
- **Coordinate Misalignment:** Inaccurate grid coordinates logged by field offices can lead to spatial misallocation during geospatial auditing.

### 3. Pipeline Analytical Scope Disclaimer
This data engineering pipeline functions strictly as a **macro-level screening tool** to calculate statistical anomalies (such as Z-score deviations and market concentration ratios). **The findings do not establish fraud, corruption, or legal liability.** Rather, they provide evidence-based target lists to assist COA physical inspection teams in deploying on-site auditors effectively.

---

## Ethics & Responsible Data Governance

1. **Non-Accusatory Screening Principle:** Flagged anomalies (e.g., `is_high_cost_outlier = 1`) represent statistical deviations requiring investigation, not proof of wrongdoing.
2. **Public Interest & Transparency:** All data processing relies exclusively on publicly disclosed datasets (`bwandowando/dpwh-flood-control-projects`) in compliance with government open data principles.
3. **Reproducibility & Auditability:** All transformation logic must be open-source and deterministic, allowing independent reviewers and government auditors to re-run identical scripts and arrive at identical outputs.

---

## Pre-Flight Ingestion Validation Rules

Before writing raw data to the **Bronze Layer** (`data/raw/dpwh_flood_control_projects.csv`), the ingestion script (`scripts/ingest.py`) must execute the following automated validation checks:

```python
def validate_preflight_schema(df: pd.DataFrame) -> bool:
    """Executes mandatory pre-flight checks on ingested raw dataframe."""
    required_columns = [
        "ProjectId", "DistrictEngineeringOffice", "ContractCost", 
        "Contractor", "Province", "Region", "CompletionDate"
    ]
    
    # 1. Verify required column existence
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"❌ Ingestion Failed: Missing mandatory columns: {missing_cols}")
        
    # 2. Verify non-empty dataset
    if len(df) == 0:
        raise ValueError("❌ Ingestion Failed: Extracted dataset contains 0 records.")
        
    print("✅ Pre-flight validation passed: Mandatory schema and row count verified.")
    return True
