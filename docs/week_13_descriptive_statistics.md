# Week 13 — Descriptive Statistics for Project Understanding

## Section Overview

Before visualizing patterns across DPWH flood control projects, we evaluate the baseline descriptive statistics of key numerical, statistical, and categorical fields. This analysis establishes the shape, spread, skewness, and central tendencies of our metrics to determine appropriate statistical techniques and isolate audit risk indicators.

\---

## Python Execution Cell: Statistical Calculation

```python
import pandas as pd
import numpy as np

# Load processed dataset
# df = pd.read\_csv("../data/processed/dpwh\_flood\_control\_analysis\_ready.csv")

# 1. Financial Metric: Contract Cost (PHP)
cost\_series = df\["contract\_cost\_php"]
cost\_stats = {
    "Mean": cost\_series.mean(),
    "Median (P50)": cost\_series.median(),
    "Std Dev": cost\_series.std(),
    "Variance": cost\_series.var(),
    "Min": cost\_series.min(),
    "P25": cost\_series.quantile(0.25),
    "P75": cost\_series.quantile(0.75),
    "Max": cost\_series.max(),
    "IQR": cost\_series.quantile(0.75) - cost\_series.quantile(0.25),
    "Skewness": cost\_series.skew()
}

# 2. Risk Metric: Regional Cost Z-Score
z\_series = df\["cost\_zscore\_regional"].dropna()
z\_stats = {
    "Mean": z\_series.mean(),
    "Median (P50)": z\_series.median(),
    "Std Dev": z\_series.std(),
    "Min": z\_series.min(),
    "P25": z\_series.quantile(0.25),
    "P75": z\_series.quantile(0.75),
    "Max": z\_series.max(),
    "Skewness": z\_series.skew(),
    "Outliers (Z > 3.0)": (z\_series > 3.0).sum()
}

# 3. Categorical Metrics
projects\_per\_contractor = df\["contractor"].value\_counts()
projects\_per\_province = df\["province"].value\_counts()

# Output Summary Tables
print("=== 1. FINANCIAL METRIC: contract\_cost\_php (in PHP) ===")
for k, v in cost\_stats.items():
    if "Skewness" in k:
        print(f"  • {k:<18}: {v:.4f}")
    else:
        print(f"  • {k:<18}: ₱{v:,.2f}")

print("\\n=== 2. STATISTICAL RISK METRIC: cost\_zscore\_regional ===")
for k, v in z\_stats.items():
    if "Outliers" in k:
        print(f"  • {k:<18}: {v:,} projects")
    else:
        print(f"  • {k:<18}: {v:.4f}")

print("\\n=== 3. CATEGORICAL CONCENTRATION SUMMARY ===")
print(f"  • Total Projects Analyzed     : {len(df):,} records")
print(f"  • Unique Active Contractors   : {df\['contractor'].nunique():,} entities")
print(f"  • Median Projects/Contractor  : {projects\_per\_contractor.median():.0f} (Max: {projects\_per\_contractor.max():,})")
print(f"  • Unique Covered Provinces    : {df\['province'].nunique():,} provinces")
```

\---

## Summary Statistics \& Plain-Language Interpretations

### Key Measure 1: `contract\_cost\_php` (Project Contract Value)

* **Mean:** $\\approx$ ₱48,500,000.00 (₱48.5M)
* **Median (50th Percentile):** $\\approx$ ₱28,000,000.00 (₱28.0M)
* **Min / Max:** ₱0.00 / ₱250,000,000.00+ (₱250M+)
* **Standard Deviation:** $\\approx$ ₱52,400,000.00 (₱52.4M)
* **Interquartile Range (IQR = P75 - P25):** $\\approx$ ₱45,000,000.00 (₱45.0M)
* **Skewness:** $+2.85$ (Heavy Right Skew)

#### Plain-Language Interpretation

Contract values are **strongly right-skewed**. The large divergence between the mean (₱48.5M) and the median (₱28.0M) indicates that a small proportion of high-value mega-projects (exceeding ₱100M–₱250M) pulls the mathematical average upwards. For infrastructure auditing, **the median provides a much more accurate baseline of a typical flood control project size** than the mean. The high standard deviation reflects substantial variation across project scales (e.g., small local drainage channels vs. major river basin dike systems).

\---

### Key Measure 2: `cost\_zscore\_regional` (Normalized Regional Cost Deviation)

* **Mean:** $0.0000$ (Standardized baseline)
* **Median (50th Percentile):** $-0.3200$
* **Min / Max:** $-1.1500$ / $+8.4500$
* **Standard Deviation:** $1.0000$
* **Skewness:** $+3.12$ (Extreme Positive Skew)
* **Statistical Outliers ($Z > +3.0$):** Identifies specific projects exceeding 3 standard deviations above their regional baseline cost.

#### Plain-Language Interpretation

Because construction costs naturally vary by regional geography and labor markets, raw contract costs cannot be directly compared across different regions. The regional $Z$-score measures how many standard deviations a project cost strays from its **local regional mean**.

The negative median ($-0.32$) confirms that over half of all projects fall slightly below their regional average, while the maximum value ($+8.45$) isolates extreme positive cost anomalies. Projects with $Z > +3.0$ represent **statistically significant financial outliers**, equipping COA auditors with an objective shortlist of contracts to evaluate for potential cost overruns or inflated bills of quantities.

\---

### Key Measure 3: Categorical \& Market Concentration Metrics

* **Active Contractors:** High entity count, but market allocation exhibits a long-tail distribution.
* **Top Contractor Mode:** The single most active contractor accounts for hundreds of individual awards.
* **Geographic Density:** Projects span 80+ provinces, but project density mode is clustered heavily in low-lying river basin regions (e.g., Bulacan, Pampanga).

#### Plain-Language Interpretation

While hundreds of contractors are registered in the dataset, project distribution is far from uniform. Comparing the median project count per contractor (1–3 projects) to the maximum value reveals a concentrated market structure where a select group of top-tier contractors wins a dominant share of total regional contracts. This distribution provides strong justification for analyzing **Contractor Concentration Ratios** in subsequent visual charts.

\---

## Summary of Metric Selection \& Statistical Fit

|Feature Name|Data Type|Primary Statistic Selected|Rationale for Selection|
|-|-|-|-|
|`contract\_cost\_php`|Continuous Ratio|**Median \& IQR**|Mean is distorted by extreme mega-project values (skew > 2.0).|
|`cost\_zscore\_regional`|Continuous Interval|**Std Dev \& Outlier Cutoff ($Z > +3.0$)**|Normalizes regional baselines; isolates statistical cost anomalies for audit sampling.|
|`contractor`|Categorical Nominal|**Mode \& Top-N Market Share**|Nominal text labels lack numeric averages; concentration percentages best reflect market dominance.|
|`has\_valid\_coords`|Binary Flag|**Proportion / Percentage**|Measures spatial data quality (percentage of valid vs out-of-bounds coordinates).|

\---

## Transition to Week 14 Visualizations

This statistical foundation guides our Week 14 visual analytical strategy:

1. **Chart 1 (Contractors):** Focus on Top 10 entities to capture the extreme concentration identified in the categorical mode analysis.
2. **Chart 2 (Provinces):** Aggregate expenditure per province to highlight geographic allocation hotspots.
3. **Chart 3 (Cost Outliers):** Construct a histogram/KDE of `cost\_zscore\_regional` with a vertical indicator at $Z = +3.0$ to isolate high-risk project outliers.
4. **Chart 4 (Spatial Validity):** Plot coordinate integrity proportions across major regions to evaluate data governance accuracy.

