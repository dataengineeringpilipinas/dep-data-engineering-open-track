# Public Data Patterns in DPWH Flood Control Projects (2022–2025)

## Problem Statement

I want to answer:
**"Can publicly available DPWH flood control project data reveal unusual geographic, financial, and contractor-related patterns that may indicate areas requiring further audit or investigation between 2022 and 2025?"**

My hypothesis is that while most flood control projects are distributed according to infrastructure and disaster mitigation needs, the data may reveal patterns that warrant closer examination. These patterns could include unusually high contractor concentration, cost anomalies, and geographic investment hotspots.

---

## Audience

- **Primary Audience:** **Commission on Audit (COA) — Infrastructure Audit Division** (to assist in identifying high-risk geographic clusters and prioritizing physical/financial field audits).
- **Secondary Audience:** Department of Public Works and Highways (DPWH) internal oversight, Local Government Units (LGUs), investigative journalists, civil society organizations (CSOs), and citizen researchers.

---

## KPI or Key Metric

- **Primary Metric:** **Contractor Concentration Ratio** (Percentage share of total regional/provincial flood control project value awarded to top contractors).
- **Secondary / Supporting Metrics:**
  - **Cost Anomaly Z-Score:** Statistical deviation of unit/km project cost relative to regional benchmarks.
  - **Geographic Investment Density:** Total project allocation per province/municipality normalized by land area and population.
  - **Contractor Project Volume:** Total count and aggregate contract value of completed projects per contractor.

---

## Possible Final Dashboard

The dashboard should help audit teams and researchers quickly identify geographic hotspots with high contractor concentration, pinpoint cost outliers among completed projects, and filter by province, region, contractor, and year.

---

## Data Source Notes

### Primary Source
- **Name:** DPWH Flood Control Projects Dataset (Kaggle)
- **URL:** https://www.kaggle.com/datasets/bwandowando/dpwh-flood-control-projects
- **Format:** CSV
- **Coverage:** 9,855 completed DPWH flood control project records nationwide (July 2022 – May 2025)
- **Raw Data Path:** `data/raw/dpwh_flood_control_projects.csv` (Pulled: 2026-09-26)
- **Why it fits:** Provides structured, project-level metadata—including contract amounts, contractor names, project titles, coordinates, and implementing offices—enabling direct calculation of audit-relevant risk indicators.
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
2. **Silver Layer (`data/processed/`):** Standardized, deduplicated, and canonicalized dataset used for cleaning and validation.
3. **Gold Layer (`data/output/` or `data/analytics/`):** Analytical outputs used for audit screening, aggregate review, and dashboard-ready tables.

### Project Dependencies
- **Primary Python Modules:** `pandas`, `kaggle`, `pathlib`, `os`, `numpy`

---

## ETL vs ELT

This project is a simple ETL-style flow:

- **Extract:** download the raw Kaggle CSV into `data/raw/`
- **Transform:** clean and standardize the data in `scripts/transform.py`
- **Load/Analyze:** write processed outputs to `data/processed/` and produce analysis results in `data/output/analysis/`

In other words, we ingest raw data first, clean it, then create analysis outputs from the cleaned dataset. This is easier to review because each stage has a clear input and output.

---

## Repository Layout

```text
.
├── data/
│   ├── raw/                     # source files downloaded from Kaggle
│   ├── processed/               # cleaned/transformed CSVs
│   └── output/                 # analysis outputs and review artifacts
├── notebooks/
│   └── data_transform_report.md
├── scripts/
│   ├── ingest.py               # main ingestion entry point
│   ├── injest.py               # compatibility alias / older script name
│   ├── transform.py            # cleaning and transformation
│   └── analysis/
│       └── analyze_silver.py   # analysis step using the cleaned dataset
├── README.md
├── requirements.txt
└── sql/
```

---

## How To Run

Follow the pipeline in order below.

### 1) Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Configure Kaggle credentials

The ingestion script requires Kaggle API credentials. Set them in your environment before running the pipeline:

```bash
export KAGGLE_USERNAME="your_kaggle_username"
export KAGGLE_KEY="your_kaggle_api_key"
```

If you prefer, you can also place your credentials in `~/.kaggle/kaggle.json`.

### 3) Run ingestion

```bash
python scripts/ingest.py
```

This downloads the raw dataset into:

```text
data/raw/dpwh_flood_control_projects.csv
```

### 4) Run transformation

```bash
python scripts/transform.py
```

This reads the raw file and saves the cleaned dataset to:

```text
data/processed/dpwh_flood_control_projects_cleaned.csv
```

### 5) Run analysis

```bash
python scripts/analysis/analyze_silver.py \
  --input data/processed/dpwh_flood_control_projects_cleaned.csv \
  --output-dir data/output/analysis
```

The analysis script generates review-oriented outputs such as:
- `projects_by_region.csv`
- `projects_by_province.csv`
- `projects_by_contractor.csv`
- `projects_for_review.csv`
- `silver_analysis_summary.txt`

### Pipeline flow summary

```text
raw dataset
   ↓
python scripts/ingest.py
   ↓
data/raw/dpwh_flood_control_projects.csv
   ↓
python scripts/transform.py
   ↓
data/processed/dpwh_flood_control_projects_cleaned.csv
   ↓
python scripts/analysis/analyze_silver.py --input ... --output-dir ...
   ↓
data/output/analysis/
```

---

## Data Quality & Investigation Limitations Disclaimer

- `Self-Reported Data Vulnerabilities`: **This dataset reflects DPWH's self-reported submissions, which have been subject to formal Senate Blue Ribbon Committee inquiry and internal DPWH validation efforts.**
- `Validation Context`: **As of DPWH internal validation efforts in late 2025, 15 projects out of 1,600 validated sites were confirmed non-existent, with roughly 160 locations pending verification.**
- `Analytical Scope`: **Findings from this project serve as data-driven indicators warranting further physical verification and audit, not definitive proof of legal wrongdoing or fraud.**

---

## Definition of Done for Week 12

A reviewer should be able to:

1. install the project dependencies,
2. download the raw Kaggle dataset,
3. run the cleaning/transform step,
4. execute the analysis step,
5. understand exactly where each output is written.

The repository now follows a clear and reproducible project flow from raw input to analysis output.
