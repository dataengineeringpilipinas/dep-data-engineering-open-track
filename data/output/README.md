# Analysis folder

This folder contains the final review and summary outputs generated after the cleaned dataset has been produced.

## Files produced

- `projects_by_region.csv`
- `projects_by_province.csv`
- `projects_by_contractor.csv`
- `projects_by_funding_year.csv`
- `projects_for_review.csv`
- `analysis_summary.txt`

## How to run

```bash
python scripts/analysis/analyze_silver.py \
  --input data/processed/dpwh_flood_control_projects_cleaned.csv \
  --output-dir data/output/analysis
```

This script reads from the processed dataset and writes grouped audit-ready outputs into `data/output/analysis/`.
