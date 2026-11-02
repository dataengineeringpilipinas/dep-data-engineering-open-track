# Public Data Patterns in DPWH Flood Control Projects (2022–2025)

## Project goal

This project analyzes DPWH flood control project data to look for geographic, financial, and contractor patterns that may warrant audit follow-up or deeper review.

## Repository structure

```text
.
├── data/
│   ├── raw/              # downloaded source CSVs from Kaggle
│   ├── processed/        # cleaned and normalized data for modeling/analysis
│   └── output/           # analysis-ready outputs
├── notebooks/
│   └── data_transform_report.md
├── scripts/
│   ├── ingest.py         # download raw dataset
│   ├── injest.py         # compatibility alias (deprecated)
│   ├── transform.py      # clean and standardize data
│   └── analysis/
│       └── analyze_silver.py
├── README.md
├── requirements.txt
├── sql/
└── dashboard/
```

## ETL flow

This repo follows a simple ETL-style workflow:

1. Extract: download raw data into `data/raw/`
2. Transform: clean and standardize it in `scripts/transform.py`
3. Load / Analyze: save processed output and analytical summaries in `data/processed/` and `data/output/`

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

You can also store them in `~/.kaggle/kaggle.json`.

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

This creates a cleaned output such as:

```text
data/processed/dpwh_flood_control_projects_cleaned.csv
```

### 5) Run analysis

```bash
python scripts/analysis/analyze_silver.py \
  --input data/processed/dpwh_flood_control_projects_cleaned.csv \
  --output-dir data/output/analysis
```

This generates review-oriented output files in `data/output/analysis/`.

## Pipeline summary

```text
raw data
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

## Notes for reviewers

- The repo follows a clear raw-to-processed-to-analysis flow.
- The canonical ingestion script is `scripts/ingest.py`.
- `scripts/injest.py` remains only as a compatibility wrapper and should not be used for new work.
- Keep data artifacts under `data/` and executable logic under `scripts/`.

## Data quality and audit note

This dataset is self-reported and should be treated as a screening tool for audit follow-up, not as proof of wrongdoing.
