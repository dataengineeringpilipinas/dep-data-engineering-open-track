# DPWH Flood Control Projects Audit Signals

This repository is my personal implementation of the Data Engineering Pilipinas Open Track, focused on the Phase 3 / Milestone 3 requirement: a clean, reproducible, auditable dataset pipeline.

## Project question

Can publicly available DPWH flood control project data reveal geographic, financial, and contractor-related patterns that deserve closer audit review?

## Audience

- Commission on Audit (COA) infrastructure audit teams
- DPWH internal oversight reviewers
- civic and investigative researchers
- local data practitioners building an audit-oriented data project

## Data source

- Dataset: DPWH Flood Control Projects (Kaggle)
- Source URL: https://www.kaggle.com/datasets/bwandowando/dpwh-flood-control-projects
- Format: CSV
- Coverage: nationwide DPWH flood control project records from 2022 to 2025
- Raw file path: `data/raw/dpwh_flood_control_projects.csv`

## Project goal

This project builds a clean and reviewable dataset for identifying:

- contractor concentration patterns
- geographic hotspots of project spending
- unusually high or low contract cost signals
- office-level project patterns worthy of follow-up review

## Repository structure

```text
.
├── data/
│   ├── raw/                  # source CSV downloaded from Kaggle
│   ├── processed/           # cleaned project dataset
│   ├── output/              # analysis/export files
│   └── README.md
├── notebooks/
│   └── data_transform_report.md
├── scripts/
│   ├── ingest.py            # download raw dataset
│   ├── injest.py            # compatibility alias
│   ├── transform.py         # cleaning and validation
│   └── analysis/
│       └── analyze_silver.py
├── sql/
│   ├── README.md
│   ├── schema_ddl.sql
│   └── business_questions.sql
├── dashboard/
│   └── README.md
├── requirements.txt
├── README.md
└── .gitignore
```

## DEP milestone alignment

This repo follows the DEP track milestones for a data project:

- M2: ingestion script + raw dataset landed in `data/raw/`
- M3: clean dataset + data quality checks + SQL business questions + reproducible pipeline

## Pipeline flow

```text
1. Download raw source
   python scripts/ingest.py

2. Clean and validate data
   python scripts/transform.py

3. Analyze cleaned data
   python scripts/analysis/analyze_silver.py \
     --input data/processed/dpwh_flood_control_projects_cleaned.csv \
     --output-dir data/output/analysis
```

## Data processing notes

The transformation step performs the following:

- standardize column names
- clean string fields
- convert numeric columns safely
- remove exact duplicate rows
- validate row count and key integrity
- write the cleaned output to `data/processed/`

## SQL deliverable

The project includes SQL files in `sql/` to answer core business questions, including:

- top contractors by contract value
- provinces with the highest project spend
- district engineering offices with the highest average project costs

See:
- `sql/business_questions.sql`
- `sql/schema_ddl.sql`

## How to run the project

### 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Set Kaggle credentials

```bash
export KAGGLE_USERNAME="your_kaggle_username"
export KAGGLE_KEY="your_kaggle_api_key"
```

Or place them in `~/.kaggle/kaggle.json`.

### 3) Run ingestion

```bash
python scripts/ingest.py
```

### 4) Run transformation

```bash
python scripts/transform.py
```

### 5) Run analysis

```bash
python scripts/analysis/analyze_silver.py \
  --input data/processed/dpwh_flood_control_projects_cleaned.csv \
  --output-dir data/output/analysis
```

## Data quality and audit note

This dataset is self-reported and should be treated as a screening tool for audit follow-up, not as proof of wrongdoing.

## Milestone 3 completion status

This repo includes the key M3 items:

- processed dataset saved in `data/processed/`
- cleaning logic and validation checks
- schema planning and SQL query deliverables
- repeatable pipeline structure for reviewers
- clear run instructions
