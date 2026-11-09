# Data

| Folder | Contents | Made by |
|---|---|---|
| `raw/` | `dpwh_flood_control_projects.csv` (raw, unmodified) and `SOURCE.md` (source URL, download date) | `scripts/ingest.py` |
| `processed/` | `dpwh_flood_control_projects_cleaned.csv` (cleaned, 9,855 rows) | `scripts/transform.py` |
| `processed/` | `dpwh_flood_control_analysis_ready.csv` (one row per project, 9,827 rows) | `scripts/advanced_transform.py` |
| `processed/` | `m5_*.csv` (segments, KPIs, province concentration, review shortlist) | `scripts/analysis/m5_segmentation_kpis.py` |

Raw data is never edited. Everything in `processed/` can be rebuilt from the raw file with `python scripts/run_pipeline.py`.
