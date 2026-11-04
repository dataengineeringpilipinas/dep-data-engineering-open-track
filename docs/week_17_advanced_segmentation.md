# Week 17 — Advanced Segmentation & Cohort Analysis (Path B)

## Path choice

Path B. The project question asks where unusual patterns may justify further audit. That is a description and prioritisation problem, so a predictive model would be forced.

## Segmentation plan

| Segment Dimension | Why It Matters | Comparison Metric |
|---|---|---|
| Island group × completion-year cohort | Tests whether geography or timing explains where costly projects appear | High-cost outlier rate, average cost |
| Type of work × island group | Different structures cost different amounts | Average cost, outlier rate |
| Contractor size tier (projects won) | Shows whether value sits with occasional or repeat winners | Share of projects and of value |

## Key findings

- The original outlier rate rises with completion year in every island group (Luzon 0.7% in 2022 to 7.2% in 2024). A time-adjusted flag (compared within region and completion year) stays in a narrow band, so most of the rise reflects costs increasing over time.
- Project type changes the cost level (drainage about PHP 23.5M vs revetment about PHP 66.8M), so cost flags should eventually be benchmarked by type.
- 85 contractors that won 21+ projects hold 38.8% of contract value; 1,157 single-project contractors hold 9.5%.

## Where the work lives

- Calculations: `scripts/analysis/m5_segmentation_kpis.py`
- Narrative and charts (Charts 6–7): `notebooks/M5_segmentation_kpis_brief.ipynb`, section 1
- Outputs: `data/processed/m5_segment_*.csv`

## Definition of done check

- [x] Correct path section completed (Path B)
- [x] Segments compared and tied to the project question
- [x] Results explained, with small cells flagged as unreliable
