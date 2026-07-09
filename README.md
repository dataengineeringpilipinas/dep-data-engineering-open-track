# Philippine Fuel Price Data Pipeline

## Problem Statement
I want to answer: "How have Philippine retail fuel prices (gasoline, diesel, kerosene) changed over time, and how do they vary by region and fuel type?"

## Audience
This project is for consumers, journalists and researchers, and technical reviewers (recruiters, hiring managers, data engineers) evaluating real-world Data Engineering skills.

## KPI or Key Metric
The main metric I want to track is average retail price per liter, by fuel type and region, over time, with week-over-week percent change as a secondary derived metric.

## Likely Data Source
I will explore the DOE Oil Monitor bulletins and GlobalPetrolPrices.com's Philippines gasoline series.
DOE Oil Monitor: https://doe.gov.ph/articles/group/liquid-fuels?category=Oil+Monitor&display_type=Card
GlobalPetrolPrices.com: https://www.globalpetrolprices.com/Philippines/gasoline_prices/

## Possible Final Dashboard
The dashboard should help the audience quickly see current DOE prices, historical trends by fuel type, and regional comparisons, enough to answer "is now a good time to fill up, and how does my region compare?" at a glance.

## Data Source Notes

### Primary Source
- Name: DOE Oil Monitor (Department of Energy, Philippines)
- URL: https://doe.gov.ph/articles/group/liquid-fuels?category=Oil+Monitor&display_type=Card
- Format: PDF bulletins (published weekly as attachments on the listing page)
- Coverage: Prevailing pump prices by fuel type (gasoline, diesel, kerosene), by oil company/brand, and by region, historically back several years via pagination
- Why it fits the problem: This is the authoritative primary source for Philippine fuel prices, with the brand- and region-level granularity needed to answer the problem statement
- Known limitations: Filenames are inconsistent (varying formats, occasional revision suffixes) and require tolerant date parsing; publish cadence is a voluntary weekly norm, not guaranteed, so ingestion must poll and diff rather than assume one file per week; the site blocks naive automated HTTP fetches (bot detection), so ingestion will need realistic headers, session handling, or headless-browser fallback

### Fallback Source
- Name: GlobalPetrolPrices.com — Philippines Gasoline Prices
- URL: https://www.globalpetrolprices.com/Philippines/gasoline_prices/
- Format: CSV/API (downloadable data, weekly series)
- Coverage: Weekly Octane-95 gasoline price for the Philippines, national aggregate, from 2015-12-28 to present, sourced from the DOE
- Why it could still work: If the primary DOE source is temporarily blocked or a bulletin is missing, this provides a continuous, DOE-sourced weekly price series to fill gaps or cross-validate extracted values
- Known limitations: Single national aggregate value only — no brand or regional breakdown, and no diesel/kerosene series, so it cannot fully substitute for the primary source, only supplement it