# Week 18 — KPI Development & Metric Framework (Path B)

## KPI framework

| KPI | Definition | Formula or Logic | Why It Matters |
|---|---|---|---|
| KPI 1 — High-cost outlier rate | Share of completed projects unusually costly for their region | flagged projects ÷ all projects (also time-adjusted) | Financial pattern |
| KPI 2 — Average contract cost | Mean contract cost per project (PHP millions) | total cost ÷ number of projects | Context for KPI 1 |
| KPI 3 — Top-10 contractor share of value | Share of value held by the ten largest contractors | top-10 value ÷ total value | National contractor pattern |
| KPI 4 — Provincial top-contractor share | Largest contractor's share of a province's value (median over provinces with 30+ projects) | largest contractor value ÷ province value | Local concentration |
| KPI 5 — Over-budget rate | Share of contracts costing more than the approved budget | cost > budget ÷ contracts with a budget | Financial control signal |

Total project count and total cost by region are kept as context, not KPIs, because they mostly reflect region size.

## Headline values

KPI 1: 3.3% · KPI 2: PHP 55.5M · KPI 3: 10.3% · KPI 4: 18.6% (69 provinces) · KPI 5: 7.9%

## Trend over time (by completion quarter)

- KPI 1 rises from 0.6% (2022 Q3) to 9.4% (2025 Q1), but the time-adjusted version stays between about 1.5% and 5%, while KPI 2 rises from PHP 33.4M to PHP 76.1M. Read KPI 1 next to KPI 2 or in its time-adjusted form.
- KPI 3 holds at 13–18% through 2024; 2025 quarters have few projects (309 and 67) and are not a trend.
- KPI 5 drifts down from 10.2% to about 6–9%.

## Where the work lives

- `scripts/analysis/m5_segmentation_kpis.py` (`kpi_quarterly`, `kpi_summary`, `province_concentration`, `review_shortlist`)
- `notebooks/M5_segmentation_kpis_brief.ipynb`, section 2 (Chart 8–9)
- Outputs: `data/processed/m5_kpi_quarterly.csv`, `m5_kpi_summary.csv`, `m5_review_shortlist.csv`
