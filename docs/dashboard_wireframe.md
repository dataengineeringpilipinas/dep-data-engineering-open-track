# Dashboard Wireframe and Layout Plan (Week 21)

**Audience:** audit teams (COA), DPWH oversight, researchers and journalists.
**Core question:** Can public data show where geographic, financial and contractor patterns may justify a closer audit look?

## KPIs shown (5, all defined in the M5 notebook)

| KPI | Question it answers |
|---|---|
| KPI 1 — High-cost outlier rate | How common are unusually costly projects? |
| KPI 2 — Average contract cost | Are costs themselves drifting over time? |
| KPI 3 — Top-10 contractor share | Is value concentrated nationally? |
| KPI 4 — Provincial top-contractor share | Is value concentrated locally? |
| KPI 5 — Over-budget rate | How often does a contract exceed its approved budget? |

## Page layout

| # | Section | Content | Question answered | Data input | Interaction |
|---|---|---|---|---|---|
| 1 | Overview | 5 KPI cards | What are the headline numbers? | `m5_kpi_summary.csv` | Static |
| 2 | Trends | 4 quarterly line charts (KPI 1, 2, 3, 5); low-volume quarters ringed | Is the share of unusual projects really rising? | `m5_kpi_quarterly.csv` | Hover for values |
| 3 | Segments | Island × year outlier-rate table; contractor size tiers | Do geography, timing or contractor size explain the pattern? | `m5_segment_*.csv` | Static |
| 4 | Hotspots | Region and province filters, concentration map, concentration ranking, outlier scatter, project table, regional summary | Where are the hotspots, and which project IDs should be reviewed? | `m5_province_concentration.csv`, analysis-ready CSV | Filters, click to flag, copy IDs |
| 5 | Shortlist and insight | Six-province review shortlist, four key insights | Where should auditors look first? | `m5_review_shortlist.csv` | Static |
| 6 | Method | Limitations and links to the repo | What should the reader be careful about? | — | Static |

## Sketch

```text
+----------------------------------------------------------+
| Title · question · caution · section links               |
+----------------------------------------------------------+
| [KPI 1] [KPI 2] [KPI 3] [KPI 4] [KPI 5]                  |
+----------------------------------------------------------+
| Trends:  [KPI 1 lines]  [KPI 2]                          |
|          [KPI 3]        [KPI 5]                          |
+----------------------------------------------------------+
| Segments: [island x year table]  [contractor tiers]      |
+----------------------------------------------------------+
| Filters: [Region v] [Province v] [Reset]                 |
| [Map]                 [Concentration ranking]            |
| [Outlier scatter]     [Projects to review + flag list]   |
| [Regional summary table]                                 |
+----------------------------------------------------------+
| Shortlist table       | Key insights                     |
+----------------------------------------------------------+
| Method and limitations                                   |
+----------------------------------------------------------+
```

## Interactive vs static

- **Interactive:** filters, map click, flagging projects and copying IDs (section 4 only), hover tooltips.
- **Static:** everything else, to keep the story readable.

## Choices made

- Charts from the notebooks that do not answer the question (for example the raw regional bars) are left out.
- The map is a bubble map at provincial capitals because the data has coordinates but no province boundaries.
- Total project count and cost by region are context in the regional table, not KPI cards.
