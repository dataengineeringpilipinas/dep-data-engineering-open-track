# Demo Script (about 7 minutes)

Live dashboard: https://michaelbacus-lab.github.io/dep-data-engineering-open-track/

## 1. Problem and audience (1 min)

- "After the flood control spending controversy, I asked: can public project data show where an auditor should look first?"
- Audience: COA audit teams, DPWH oversight, researchers and journalists.
- Say up front: the data can point to leads, it cannot prove wrongdoing.

## 2. Data source and pipeline (1.5 min)

- Source: Kaggle DPWH flood control dataset, 9,855 completed projects, July 2022 to May 2025.
- Pipeline: raw CSV, clean and standardise, build an analysis-ready table (9,827 projects), compute segments and KPIs, build the dashboard.
- One command reproduces it: `python scripts/run_pipeline.py`.

## 3. Key findings (2 min)

1. The leads are local. No contractor holds more than about 1.5% nationally, but in some provinces one contractor holds 36% to 41% of value (Marinduque, Bukidnon, Romblon, Abra).
2. Costs rose over time, from an average of PHP 33M in mid-2022 to PHP 76M in early 2025. My first outlier flag rose with it, so I added a time-adjusted flag. That is the main lesson: check that a pattern is not just an artefact of timing.
3. Region IV-B, led by Oriental Mindoro, still has the highest flag rate after the adjustment.

## 4. Dashboard walkthrough (2 min)

1. KPI cards: five headline numbers.
2. Trends: point at the gap between the original and time-adjusted outlier rate.
3. Hotspots: choose Region IV-B, click Oriental Mindoro, flag a project from the table, press Copy flagged IDs.
4. Shortlist: six provinces where concentration and cost flags overlap.

## 5. Limitations and next steps (0.5 min)

- Limits: completed projects only, flags not benchmarked by project type, truncated contractor names.
- Next: clean contractor names, normalise with PSA population data, validate shortlisted projects against DPWH Project DIME and COA reports.

## Likely questions

| Question | Short answer |
|---|---|
| Does this prove corruption? | No. These are statistical indicators for prioritising review. |
| Why not a prediction model? | The question is about where to look first, which is a description and prioritisation problem. |
| Why the 30-project cut-off? | Small provinces give noisy concentration figures, and a single large contract can swing the share. |
| Can I rerun it? | Yes: install requirements and run `python scripts/run_pipeline.py`. |
