# Dashboard

`index.html` is the deployable dashboard: one self-contained page with its data embedded, so it needs no server or extra files.

- **Live:** https://michaelbacus-lab.github.io/dep-data-engineering-open-track/
- **Rebuild:** `python scripts/build_dashboard.py` (reads `data/processed/`, writes `dashboard/index.html`). Do not edit `index.html` by hand; edit the template in `build_dashboard.py` and rebuild.
- **Publish:** pushing changes under `dashboard/` to `main` runs `.github/workflows/pages.yml`, which deploys this folder to GitHub Pages. One-time setup: repository **Settings → Pages → Source: GitHub Actions**.
- **Open locally:** double-click `index.html`, or run `python -m http.server -d dashboard` and visit http://localhost:8000

The layout plan is in [`docs/dashboard_wireframe.md`](../docs/dashboard_wireframe.md).
