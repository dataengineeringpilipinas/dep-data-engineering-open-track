# Dashboard folder

This folder is reserved for dashboard-related outputs and presentation assets.



\# Dashboard



`index.html` is the deployable dashboard: one self-contained page with its data embedded, so it needs no server or extra files.



\- \*\*Live:\*\* https://michaelbacus-lab.github.io/dep-data-engineering-open-track/

\- \*\*Rebuild:\*\* `python scripts/build\_dashboard.py` (reads `data/processed/`, writes `dashboard/index.html`)

\- \*\*Publish:\*\* pushing changes under `dashboard/` to `main` runs `.github/workflows/pages.yml`, which deploys this folder to GitHub Pages.

\- \*\*Open locally:\*\* double-click `index.html`, or run `python -m http.server -d dashboard` and visit http://localhost:8000



## Current purpose

* store dashboard-ready outputs
* keep visual artifacts separate from source and processed data
* maintain a clean project layout for reviewer handoff

## Notes

Dashboard work should stay distinct from the raw ingestion and transformation pipeline so the project remains easy to audit.

