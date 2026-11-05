# Week 22 — Dashboard Build & GitHub Pages Setup

## Build

- `scripts/build_dashboard.py` reads `data/processed/` and writes `dashboard/index.html`, a single self-contained page with its data embedded.
- Output path is fixed and repeatable: `dashboard/index.html`.
- It is part of the pipeline: `python scripts/run_pipeline.py`.

## Deployment target

- GitHub Pages, deployed by `.github/workflows/pages.yml`, which publishes the `dashboard/` folder whenever it changes on `main`.
- One-time setup in the repo: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
- Expected URL: https://michaelbacus-lab.github.io/dep-data-engineering-open-track/

## Definition of done check

- [x] Dashboard generated locally and opens in a browser
- [x] Deployment target configured
- [x] File path clear and repeatable
- [x] Charts match the planned KPIs
