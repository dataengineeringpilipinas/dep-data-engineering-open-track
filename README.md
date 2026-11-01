# Public Data Patterns in DPWH Flood Control Projects (2022–2025)

## Problem Statement

I want to answer:
**"Can publicly available DPWH flood control project data reveal unusual geographic, financial, and contractor-related patterns that may indicate areas requiring further audit or investigation between 2022 and 2025?"**

My hypothesis is that while most flood control projects are distributed according to infrastructure and disaster mitigation needs, the data may reveal patterns that warrant closer examination. These may include unusually high concentrations of projects within specific provinces, repeated awards to the same contractors, or significant differences in project costs across comparable locations. Such patterns do **not** establish corruption, fraud, or wrongdoing. Instead, they provide evidence-based indicators that can help auditors, policymakers, journalists, and citizens identify projects that deserve further review. If the analysis finds no unusual concentrations or inconsistencies, it would suggest that the observed project distribution is generally consistent with available public data. If notable anomalies are identified, the findings could support stronger transparency initiatives, more detailed public reporting, and more targeted oversight by government auditing agencies.

---

## Audience

- **Primary Audience:** **Commission on Audit (COA) — Infrastructure Audit Division** (to assist in identifying high-risk geographic clusters and prioritizing physical/financial field audits).
- **Secondary Audience:** Department of Public Works and Highways (DPWH) internal oversight, Local Government Units (LGUs), investigative journalists, civil society organizations (CSOs), and citizens interested in infrastructure transparency.

---

## KPI or Key Metric

- **Primary Metric:** **Contractor Concentration Ratio** (Percentage share of total regional/provincial flood control project value awarded to top contractors).
- **Secondary / Supporting Metrics:**
  - **Cost Anomaly Z-Score:** Statistical deviation of unit/km project cost relative to regional benchmarks.
  - **Geographic Investment Density:** Total project allocation per province/municipality normalized by land area and population.
  - **Contractor Project Volume:** Total count and aggregate contract value of completed projects per contractor.

---

## Possible Final Dashboard

The dashboard should help audit teams and researchers quickly identify geographic hotspots with high contractor concentration, pinpoint cost outliers among completed projects, and filter by province or region to flag specific project IDs for further review. It will feature interactive choropleth maps, contractor distribution rankings, cost dispersion scatter plots, and regional summary tables.

---

## Data Source Notes

### Primary Source
- **Name:** DPWH Flood Control Projects Dataset (Kaggle)
- **URL:** https://www.kaggle.com/datasets/bwandowando/dpwh-flood-control-projects
- **Format:** CSV
- **Coverage:** 9,855 completed DPWH flood control project records nationwide (July 2022 – May 2025)
- **Raw Data Path:** `data/raw/dpwh_flood_control_projects.csv` (Pulled: 2026-09-26)
- **Why it fits:** Provides structured, project-level metadata—including contract amounts, contractor names, project titles, coordinates, and implementing offices—enabling direct calculation of contractor concentration, cost variances, and spatial distribution.
- **Known limitations:** Covers completed projects only and relies on self-reported government entries subject to ongoing coordinate inaccuracies under review.

### Fallback Source
- **Name:** DPWH Project DIME (Digital Information for Monitoring and Evaluation) Dashboard
- **URL:** https://www.dime.gov.ph/dashboard
- **Format:** HTML Web Dashboard / Downloadable Reports
- **Coverage:** National infrastructure project monitoring status
- **Why it could still work:** Acts as an independent government monitoring baseline to validate project existence, financial details, and implementation status if the primary mirror becomes unavailable.
- **Known limitations:** Field schema differs from the Kaggle dataset, requiring manual table extraction and custom field mapping.

### Secondary / Normalization Sources
- **Philippine Statistics Authority (PSA):** https://psa.gov.ph (CSV / Excel / PDF) — Provides regional population and land area data to normalize project density and cost allocation per capita.
- **Commission on Audit (COA) Annual Audit Reports:** https://www.coa.gov.ph (PDF) — Provides qualitative audit findings to cross-reference and ground statistical outliers.

---

## 🏗️ Storage Design & Data Architecture

This project follows a 3-tier **Medallion Architecture**:

1. **Bronze Layer (`data/raw/`):** Immutable raw CSV landing zone (`dpwh_flood_control_projects.csv`) ingested via manual download or Kaggle API.
2. **Silver Layer (`data/processed/`):** Standardized, deduplicated, and canonicalized Parquet dataset (cleaning contractor names, validating GPS coordinates, parsing dates, and mapping PSGC boundaries).
3. **Gold Layer (Analytics):** Analytical Star Schema aggregating contractor concentration, provincial spend per capita, and cost anomaly z-scores.

### Project Dependencies
- **Primary Python Modules:** `pandas`, `kaggle`, `pathlib`, `os`, `geopandas`

### Dimensional Data Model (Gold Layer Schema)

```mermaid
erDiagram
    dim_location ||--o{ fact_flood_control_projects : "1:N"
    dim_contractor ||--o{ fact_flood_control_projects : "1:N"
    dim_implementing_office ||--o{ fact_flood_control_projects : "1:N"

    dim_location {
        string location_id PK "PSGC Code"
        string province
        string region
        int population
        float land_area_sqkm
    }

    dim_contractor {
        string contractor_id PK "Canonical Hash Key"
        string name_raw "Original DPWH string"
        string name_clean "Deduplicated Name"
        boolean is_consortium
    }

    dim_implementing_office {
        string office_id PK "Office Hash Key"
        string office_name "e.g., Pampanga 1st DEO"
        string office_type "DEO or RO"
    }

    fact_flood_control_projects {
        string project_id PK "Surrogate Hash Key"
        string contractor_id FK
        string location_id FK
        string office_id FK
        date completion_date
        float contract_cost_php
        float cost_zscore_regional
    }
```
### Processed Data Plan & Table Specifications

**Main Fact Table:** `fact_flood_control_projects`
- **Grain:** One row = One completed DPWH flood control project contract
- **Primary Key:** `project_id`

| Column | Meaning | Expected Type |
| :--- | :--- | :--- |
| `project_id` | Unique identifier generated from contract title and ID metadata | String |
| `contractor_id` | Identifier for the winning contractor or joint venture | String |
| `location_id` | Standard Geographic Code (PSGC) linking to province/municipality | String |
| `office_id` | Identifier for the implementing DPWH District Engineering Office | String |
| `contract_cost_php` | Total reported project contract cost in Philippine Pesos | Float |
| `completion_date` | Date the project was logged as completed | Date |
| `cost_zscore_regional` | Statistical deviation of project cost relative to regional mean | Float |
| `latitude` | Validated GPS latitude coordinate | Float |
| `longitude` | Validated GPS longitude coordinate | Float |

...

### Related Dimensions
- `dim_contractor` : **Joins on** `contractor_id` **to aggregate contractor market concentration ratios (top-N share) and total contract volume.**
- `dim_location` : **Joins on** `location_id` **to pull PSA provincial population and land area for normalizing spend per capita.**
- `dim_implementing_office` : **Joins on** `office_id` **to categorize projects by District Engineering Office (DEO) versus Regional Office (RO).**

## 💻 Quickstart & Ingestion

### Setup Environment

Bash
#### Clone the repository
git clone https://github.com/michaelbacus-lab/dep-data-engineering-open-track.git
cd dep-data-engineering-open-track

#### Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

#### Install requirements
pip install -r requirements.txt

### Run Raw Ingestion

Bash
 python scripts/ingest.py 

## ⚠️ Data Quality & Investigation Limitations Disclaimer
- `Self-Reported Data Vulnerabilities`: **This dataset reflects DPWH's self-reported submissions, which have been subject to formal Senate Blue Ribbon Committee inquiry and internal DPWH validation regarding coordinate accuracy and potential non-existent ("ghost") entries.**

- `Validation Context`: **As of DPWH internal validation efforts in late 2025, 15 projects out of 1,600 validated sites were confirmed non-existent, with roughly 160 locations pending verification. Additionally, Senate committee inquiries noted allegations of inaccurate grid coordinates across nationwide submissions.**

- `Analytical Scope`: **Findings from this project serve as data-driven indicators warranting further physical verification and audit, not definitive proof of legal wrongdoing or fraud.**
