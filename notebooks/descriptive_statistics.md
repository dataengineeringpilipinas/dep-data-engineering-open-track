Descriptive Statistics for Project Understanding

## Section Overview

This document presents the baseline descriptive statistics generated from the processed dataset of 9,827 DPWH flood control project records. The metrics establish central tendencies, dispersion, skewness, and market concentration baselines to inform subsequent visual analysis and risk-based audit sampling.

---

## 1. Summary Statistics Output

### 1.1 Financial Metric: `contract_cost_php` (in PHP)

| Statistic | Value |
| :--- | :--- |
| **Mean** | ₱55,326,422.29 |
| **Median (P50)** | ₱48,990,135.04 |
| **Standard Deviation** | ₱39,515,650.72 |
| **Variance** | ₱1,561,486,651,852,046.50 |
| **Minimum** | ₱0.00 |
| **25th Percentile (P25)** | ₱24,499,945.88 |
| **75th Percentile (P75)** | ₱84,905,331.30 |
| **Maximum** | ₱289,500,000.00 |
| **Interquartile Range (IQR)** | ₱60,405,385.42 |
| **Skewness** | 1.3250 |

#### Written Interpretation
Contract costs demonstrate a moderate positive right-skew (skewness = $1.3250$). The mean cost (₱55.33M) sits higher than the median (₱48.99M), indicating that a subset of high-value mega-projects pulls the mathematical average upward. The middle 50% of projects fall within an Interquartile Range of ₱60.41M (between ₱24.50M and ₱84.91M). For statistical baselines, the median of ₱48.99M represents a more robust measure of a typical project allocation than the mean.

---

### 1.2 Statistical Risk Metric: `cost_zscore_regional`

| Statistic | Value |
| :--- | :--- |
| **Mean** | -0.0000 |
| **Median (P50)** | -0.1921 |
| **Standard Deviation** | 0.9992 |
| **Minimum** | -1.7395 |
| **25th Percentile (P25)** | -0.7598 |
| **75th Percentile (P75)** | 0.7336 |
| **Maximum** | 6.6099 |
| **Skewness** | 0.9070 |
| **Outliers ($Z > 3.0$)** | 77 projects |

#### Written Interpretation
The regional $Z$-score measures standard deviations of project costs relative to their specific regional baseline mean. The negative median ($-0.1921$) indicates that more than half of all projects fall slightly below their respective regional averages. However, the maximum value of $+6.6099$ isolates significant upper-tail cost anomalies. Exactly 77 projects exceed the critical threshold of $Z > 3.0$, providing an objective shortlist of extreme financial deviations for Commission on Audit (COA) priority sampling.

---

### 1.3 Categorical Concentration Summary

| Metric | Metric Value |
| :--- | :--- |
| **Total Projects Analyzed** | 9,827 records |
| **Active Contractors** | 2,409 unique entities |
| **Median Projects per Contractor** | 2 projects (Maximum: 114) |
| **Provinces Covered** | 84 unique provinces |

#### Written Interpretation
Across 84 provinces and 2,409 active contractors, project distribution exhibits a heavy long-tail structure. While the median contractor completes only 2 projects, the top entity accounts for 114 separate contract awards. This pronounced disparity warrants calculating market concentration ratios to evaluate regional market dominance by top construction firms.

---

## 2. Metric Selection and Statistical Rationale

| Feature Name | Data Type | Primary Statistic | Rationale |
| :--- | :--- | :--- | :--- |
| `contract_cost_php` | Continuous Ratio | **Median & IQR** | Mitigates distortion from high-value mega-projects ($> ₱200\text{M}$). |
| `cost_zscore_regional` | Continuous Interval | **Outlier Count ($Z > 3.0$)** | Normalizes regional baseline differences and highlights risk outliers. |
| `contractor` | Categorical Nominal | **Mode & Top-N Market Share** | Measures contractor concentration percentages where numeric averages are invalid. |
