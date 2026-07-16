# DEP Milestone Checklist

Use this to track your progress. Milestone reviewers also use this when evaluating submissions.

Aim to submit one issue per milestone by its target deadline. A late issue remains open, receives a `late-submission` indicator, and continues through normal evaluation. If the previous milestone is still awaiting review, the new issue remains open as `waiting-on-prerequisite`; its submission time is preserved and it releases automatically after the prerequisite passes. If revisions are requested, push a new commit and comment `/recheck <40-character-hash>` on the same issue. Do not open a replacement issue.

---

## M0 — Problem Statement *(End of Week 1)*

> ⚡ **Hard gate.** If you cannot pass M0, you must not proceed. Automated checks only validate the repository snapshot; a human moderator makes the final M0 verdict.

- [ ] Problem is framed as a **specific, answerable question** (not just a topic)
- [ ] Intended audience is clearly identified
- [ ] At least one potential data source has been found and linked
- [ ] README started in your own words
- [ ] GitHub repo is public with at least one commit

**Submission:** [Open a Milestone Issue](https://github.com/dataengineeringpilipinas/dep-data-engineering-open-track/issues/new/choose)

---

## M1 — Data Source Identified / Repo Initialized *(By Week 3–4)*

> ⚡ **Gate.** Week 2 deliverable (data source) must be reviewed and marked complete before Week 3 repo setup begins. Vague sources do not pass. An M1 issue may wait in the prerequisite queue, but work must not advance until M0 passes.

- [ ] Working public repo with starter folder structure + first commit
- [ ] Chosen data source is specific and usable — not vague
- [ ] Data source documented in README (name, URL, format, coverage)
- [ ] First pull path confirmed and documented
- [ ] README data section complete

**Submission:** [Open a Milestone Issue](https://github.com/dataengineeringpilipinas/dep-data-engineering-open-track/issues/new/choose)

---

## M2 — Data Ingestion Script *(By Week 6)*

> All 3 ingestion paths are valid: API / web scraping / manual download. The deliverable format is the same regardless of path.

- [ ] Raw data landed successfully in `/data/raw/`
- [ ] Ingestion method documented (API, scraping, or manual timestamped save)
- [ ] Source URL and date recorded alongside the raw file
- [ ] Script (or documented manual process) is repeatable

**Submission:** [Open a Milestone Issue](https://github.com/dataengineeringpilipinas/dep-data-engineering-open-track/issues/new/choose)

---

## M3 — Clean Dataset *(By Week 12)*

- [ ] Schema plan documented (key tables/files, grain, identifiers, expected columns) — Week 7
- [ ] At least 3 SQL queries answering business questions from the data — Week 8
- [ ] Processed dataset saved in `/data/processed/`
- [ ] Missing values handled — dropped, filled, or flagged with a reason
- [ ] Column data types are correct (dates as dates, numbers as numbers)
- [ ] Cleaning decisions logged in README or notebook markdown
- [ ] Validation checks added to the transform flow
- [ ] Transform script produces the same output on every run

**Submission:** [Open a Milestone Issue](https://github.com/dataengineeringpilipinas/dep-data-engineering-open-track/issues/new/choose)

---

## M4 — Initial Insights *(By Week 16)*

- [ ] At least 3 charts with clear titles and labels (saved in notebook or `/output/figures/`)
- [ ] Charts directly relate back to the problem statement
- [ ] Written interpretation under each chart (2–3 sentences minimum)
- [ ] One inference section that avoids overclaiming causality
- [ ] Notebook is organized and annotated with markdown

**Submission:** [Open a Milestone Issue](https://github.com/dataengineeringpilipinas/dep-data-engineering-open-track/issues/new/choose)

---

## M5 — Public Repository / Predictive Component *(By Week 20–23)*

> ⚡ Both paths (A and B) converge here. Choose the checklist for your path.

### Path A — Predictive Track

- [ ] Baseline regression or classification model built and evaluated
- [ ] Evaluation metrics documented (RMSE/R² for regression; accuracy/precision/recall for classification)
- [ ] Improved model version with documented changes
- [ ] Predictive outputs integrated into the project pipeline
- [ ] Model assumptions and limitations documented

### Path B — Non-Predictive Alt Track

- [ ] Segmentation analysis across 2–3 dimensions with comparison views
- [ ] 3–5 KPIs defined with calculation logic and trend over time
- [ ] 1-page plain-language stakeholder brief (PDF or notebook section)
- [ ] All outputs integrated into clean, runnable pipeline

### Both Paths

- [ ] Repo is professional — a stranger can understand and run it
- [ ] `requirements.txt` present and up to date
- [ ] No unnecessary files committed

**Submission:** [Open a Milestone Issue](https://github.com/dataengineeringpilipinas/dep-data-engineering-open-track/issues/new/choose)

---

## M6 — Live Deployment *(By Week 24)*

- [ ] Dashboard or report artifact built and committed
- [ ] Project deployed to GitHub Pages (primary: [pages.github.com](https://pages.github.com)) and accessible via a public URL
- [ ] Dashboard/live URL added to the README
- [ ] All links working, no missing files, no broken outputs
- [ ] Final README covers: problem, data, pipeline, analysis, dashboard, how to run
- [ ] Short presentation or demo script prepared (5–10 minutes)

**Submission:** [Open a Milestone Issue](https://github.com/dataengineeringpilipinas/dep-data-engineering-open-track/issues/new/choose)

---

*Questions? Ask in the community Discord or reach out to your moderator.*
