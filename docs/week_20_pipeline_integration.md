# Week 20 — Pipeline Integration (Path B)

## Run order (from the repository root)

```text
1. python scripts/ingest.py                              # raw data (Kaggle credentials; skip if data/raw exists)
2. python scripts/transform.py                           # cleaned data
3. python scripts/advanced_transform.py                  # analysis-ready data
4. python scripts/analysis/m5_segmentation_kpis.py       # segments, KPIs, shortlist, Charts 6-9
5. jupyter notebook notebooks/M5_segmentation_kpis_brief.ipynb
```

Steps 2–4 run together with `python scripts/run_pipeline.py` (add `--with-ingest` to include step 1). The runner stops with a clear message if any step fails.

## Path B output checklist

- [x] Segmentation outputs saved (`data/processed/m5_segment_*.csv`)
- [x] KPI definitions documented (Week 18 doc and notebook section 2)
- [x] Stakeholder brief included (`docs/stakeholder_brief.pdf`)
- [x] `requirements.txt` updated (adds matplotlib, scipy, notebook, ipykernel)

## Assumptions and limitations

- Completed projects only, July 2022 to May 2025.
- Time-adjusted flag benchmarks by region and completion year, not by project type or size.
- Contractor names are as recorded; truncated or variant names undercount some contractors; joint ventures are not split.
- Provinces under 30 projects are excluded from concentration rankings.
- 2025 quarters have few projects, so their KPI values are not trends.

## Milestone 5 self-check

- [x] `requirements.txt` is up to date
- [x] `notebooks/` contains analysis notebooks (M4 and M5)
- [x] `data/processed/` contains all output files needed for the next phase
