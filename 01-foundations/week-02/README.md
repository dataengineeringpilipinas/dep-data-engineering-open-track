# Week 2 — Data Source Discovery & Feasibility Check

**Phase 1 — Foundations &nbsp;|&nbsp; Milestone 1 prep**

---

## This Week's Focus

Find a real data source that can answer your problem statement. Evaluate it before committing.

**Topics:**

- File formats: CSV, JSON, Excel, HTML tables
- API vs downloadable files vs scraping
- Granularity, coverage, update frequency, missing values
- Basic data dictionary thinking
- Choose one primary source and one backup

---

## Resources

**Primary:** [Data Engineering Zoomcamp](https://dezoomcamp.streamlit.app) — source/data ingestion overview

**Optional:** [Database Technology Overview](https://halvorsen.blog/documents/database/database.php)

**Datasets:** [Philippine open data sources](../../docs/RESOURCES.md) — PSA OpenSTAT, data.gov.ph, PAGASA, and more

---

## Task

Find one primary dataset and one fallback. For each, document:

- File format and coverage
- How it answers your problem statement
- Known gaps or limitations

---

## Deliverable

README section: data source(s) + source notes.

> ⚡ **Gate:** This deliverable must be reviewed and marked complete before Week 3 begins. Vague sources fail. Moderator must confirm the source is specific and usable.

**Estimated time:** 4–5 hours

## Learner Support

### Starter Script / Template

Document your primary and fallback sources in a format like this:

```md
## Data Source Notes

### Primary Source
- Name: <dataset or API name>
- URL: <your_source_url>
- Format: <csv/json/xlsx/html>
- Coverage: <dates, geography, population, rows if known>
- Why it fits the problem: <one or two sentences>
- Known limitations: <missing columns, update gaps, access limits>

### Fallback Source
- Name: <backup source name>
- URL: <backup_source_url>
- Format: <csv/json/xlsx/html>
- Coverage: <scope>
- Why it could still work: <one or two sentences>
- Known limitations: <main risks>
```

### How To Adapt This To Your Project

- Prefer sources that already contain the unit you need to analyze.
- Check whether the source is public, downloadable, and current enough for your question.
- Keep one backup source in case the primary source is blocked, incomplete, or too messy.

### Sample AI Prompts

- "Compare these two sources for my question on coverage, format, update frequency, and missing values: `<paste source notes>`."
- "Help me write a concise README data source section using these notes: `<paste notes>`."
- "What should I verify in this dataset before I commit to it as my primary source?"

### Definition of Done

- You have one specific primary source and one specific backup source.
- Both sources have URLs, formats, and coverage notes.
- Your README explains why the source can answer your project question.
- A reviewer can tell the source is real and usable, not vague.

### Common Mistakes

- Listing a website homepage instead of the actual dataset or endpoint.
- Choosing a source before checking whether the needed fields exist.
- Ignoring update frequency, geography, or time coverage.
- Picking a backup source that has the same weakness as the primary source.

### If You’re Stuck After 2 Hours

- Search for the exact metric and geography in the source, not just the topic.
- Open a sample file or endpoint and confirm the columns before committing.
- Post your source options with short pros and cons so a moderator can help you choose.
