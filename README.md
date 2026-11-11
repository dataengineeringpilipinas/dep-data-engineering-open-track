# Public Data Patterns in DPWH Flood Control Projects (2022–2025)

**Live dashboard: https://michaelbacus-lab.github.io/dep-data-engineering-open-track/**

A data engineering project built in the [DEP Data Engineering Open Track](https://github.com/dataengineeringpilipinas/dep-data-engineering-open-track). It turns public records of completed DPWH flood control projects into a clean dataset, a set of KPIs and an interactive dashboard that shows where an auditor might look first.

> The indicators here are for prioritising review. They are **not** evidence of wrongdoing, fraud or corruption.

## Problem

Can publicly available DPWH flood control project data reveal unusual geographic, financial and contractor-related patterns that may indicate areas requiring further audit or investigation between 2022 and 2025?

## Audience

- **Primary:** Commission on Audit (COA), Infrastructure Audit Division, to help prioritise high-risk areas.
- **Also:** DPWH internal oversight, local government units, investigative journalists and civil society researchers.

## Data Source

| Source | Use |
|---|---|
| [DPWH Flood Control Projects (Kaggle)](https://www.kaggle.com/datasets/bwandowando/dpwh-flood-control-projects) | Primary: one CSV file, 9,855 completed-project records (22 columns), July 2022 to May 2025. Pulled with the Kaggle API on 2026-09-26; see [`data/raw/SOURCE.md`](data/raw/SOURCE.md) |
| [DPWH Project DIME](https://www.dime.gov.ph/dashboard) | Fallback and validation baseline |
| [PSA](https://psa.gov.ph) and [COA](https://www.coa.gov.ph) | Planned normalisation and audit-report context |

Known limits: completed projects only, self-reported government entries, partly truncated contractor names.

## Pipeline

```text
data/raw/dpwh_flood_control_projects.csv        (9,855 raw rows)       ◄── scripts/ingest.py (Kaggle API)
   │  scripts/transform.py           clean names, types and dates; validation checks
   ▼
data/processed/dpwh_flood_control_projects_cleaned.csv   (9,855 rows)
   │  scripts/advanced_transform.py  one row per project; regional z-score; outlier flag
   ▼
data/processed/dpwh_flood_control_analysis_ready.csv   (9,827 projects)
   │  scripts/analysis/m5_segmentation_kpis.py
   ▼
data/processed/m5_*.csv  +  output/figures/m5_*.png
   │  scripts/build_dashboard.py
   ▼
dashboard/index.html   ──►  GitHub Pages
```

Every cleaning decision, with row counts and reasons, is in the cleaning log in [`scripts/README.md`](scripts/README.md). The three SQL business questions are in [`sql/`](sql/) (run them with `python scripts/run_sql_queries.py`). The full history of decisions by phase is in [`docs/PROJECT_LOG.md`](docs/PROJECT_LOG.md).

## Analysis

| Notebook | What it shows |
|---|---|
| [`notebooks/M4_initial_insights.ipynb`](notebooks/M4_initial_insights.ipynb) | Descriptive statistics, 5 charts, cautious inference |
| [`notebooks/M5_segmentation_kpis_brief.ipynb`](notebooks/M5_segmentation_kpis_brief.ipynb) | Segmentation, 5 KPIs with trends, review shortlist, stakeholder brief |

Main findings:

- **The leads are local.** No contractor holds more than about 1.5% of national value, but in some provinces one contractor holds 39% to 50% (Apayao 50%, Misamis Occidental 43%, Marinduque 41%, Bukidnon, Romblon and Abra about 39%). The typical province (30+ projects) is at about 19%.
- **Costs rose over time** (average PHP 33M in mid-2022 to PHP 76M in early 2025), which inflated the original outlier flag. A time-adjusted flag compares projects within the same region and year.
- **Region IV-B** has the highest outlier rate after adjustment (7.0%), led by Oriental Mindoro.
- A six-province **review shortlist** (Marinduque, Bukidnon, Romblon, Abra, Sorsogon, Northern Samar) combines high concentration with an above-median time-adjusted outlier rate.

The one-page [stakeholder brief](docs/stakeholder_brief.pdf) summarises this for non-technical readers.

## Dashboard

Open the **[live dashboard](https://michaelbacus-lab.github.io/dep-data-engineering-open-track/)**. It has five KPI cards, quarterly trends, segment views, an interactive hotspot section (region and province filters, concentration map, outlier scatter, project IDs you can flag and copy) and the review shortlist. The layout plan is in [`docs/dashboard_wireframe.md`](docs/dashboard_wireframe.md).

It is one self-contained file, [`dashboard/index.html`](dashboard/index.html), deployed by `.github/workflows/pages.yml` whenever `dashboard/` changes on `main`.

## How To Run

```bash
git clone https://github.com/michaelbacus-lab/dep-data-engineering-open-track.git
cd dep-data-engineering-open-track
pip install -r requirements.txt

python scripts/run_pipeline.py                  # clean, analyse and build the dashboard
# python scripts/run_pipeline.py --with-ingest  # also downloads the raw data (needs Kaggle credentials)

python scripts/run_sql_queries.py               # print the answers to the three SQL business questions

python -m http.server -d dashboard              # then open http://localhost:8000
jupyter notebook notebooks/                     # open the M4 and M5 notebooks
python scripts/check_links.py                   # final QA: links, required files, live URL
```

The raw CSV is included in `data/raw/`, so the pipeline runs without Kaggle credentials. Python 3.10 or newer is recommended.

## Repository Layout

```text
data/raw/          raw source data
data/processed/    cleaned, analysis-ready and m5_* result tables
scripts/           pipeline, analysis, dashboard builder, link checker
notebooks/         M4 and M5 analysis notebooks
output/figures/    saved charts
dashboard/         deployable dashboard (index.html)
docs/              weekly notes, wireframe, demo script, stakeholder brief, project log
sql/               schema and business-question queries
.github/           GitHub Pages deploy workflow and the DEP milestone self-check
```

## Limitations

- Completed projects only, July 2022 to May 2025; ongoing and cancelled projects are not in the data.
- Multi-year (MYCA) contracts appear once per funding year with the cost on only one row; each is counted once with its real cost. An earlier version recorded 27 of them at PHP 0 (corrected in November 2026: total PHP 543.7B to 545.6B, outliers 329 to 326, Samar left the shortlist). Details in [`scripts/README.md`](scripts/README.md).
- The outlier flag benchmarks by region (and region and year when time-adjusted) but not by project type or size.
- Contractor names are as recorded; truncated or variant names undercount some contractors, and joint ventures are not split.
- Provinces under 30 projects are left out of concentration rankings because the figures are noisy.
- 2025 quarters have few projects, so their KPI values are not trends.
- The map is a bubble map at provincial capitals, not a boundary map.
