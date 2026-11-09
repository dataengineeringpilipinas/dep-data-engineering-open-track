# Week 1 — Project Scoping & Problem Definition

**Project Title:** Public Data Patterns in DPWH Flood Control Projects (2022–2025)  
**Target Audience:** Commission on Audit (COA) — Infrastructure Audit Division  
**Document Path:** `docs/week01_problem_definition.md`  

---

## Executive Summary

This document establishes the project charter, problem statement, core audit hypotheses, analytical scope, and initial data source mapping for the data engineering pipeline analyzing Department of Public Works and Highways (DPWH) flood control projects completed between 2022 and 2025.

The primary goal of this project is to build an automated, reproducible data engineering and analytics pipeline that ingests public procurement and infrastructure data, standardizes project metrics, and surfaces evidence-based **Key Risk Indicators (KRIs)** to assist auditors, policy makers, journalists, and citizens in prioritizing field site investigations.

---

## Problem Statement

> **"Can publicly available DPWH flood control project data reveal unusual geographic, financial, and contractor-related patterns that may indicate areas requiring further audit or investigation between 2022 and 2025?"**

---

## Audit Hypothesis

While flood control infrastructure allocations are expected to align with geographic vulnerability, disaster mitigation urgency, and regional engineering requirements, public data may expose underlying structural anomalies. 

### Working Hypotheses
1. **Contractor Market Concentration:** A small subset of private contractors holds a dominant market share of aggregate national or regional project portfolio values.
2. **Geographic Investment Hotspots:** Funding allocations exhibit sharp statistical concentration in specific provinces or District Engineering Offices (DEOs) compared to national baseline averages.
3. **Unit Cost Variances:** Comparable flood control infrastructure types demonstrate significant cost disparities across neighboring districts or administrative regions.

> **Disclaimer:** Identified statistical anomalies do not establish corruption, fraud, or legal wrongdoing. Instead, they serve as objective, data-driven indicators to optimize the deployment of COA physical verification and audit resources.

---

## Analytical Scope & Boundaries

| Parameter | In-Scope | Out-of-Scope |
| :--- | :--- | :--- |
| **Time Horizon** | Projects logged/completed between 2022 and 2025 | Pre-2022 or uncontracted future pipeline projects |
| **Project Type** | DPWH Flood Control & Drainage Infrastructure | National roads, bridges, school buildings, or right-of-way acquisitions |
| **Data Source** | Publicly accessible DPWH disclosures (Kaggle dataset `bwandowando/dpwh-flood-control-projects`) | Confidential internal government communication or unreleased bid logs |
| **Analysis Level** | Macro-level statistical screening (Contractor, Regional, DEO, Provincial) | Technical engineering stress testing or forensic material quality analysis |

---

## Key Risk Indicators (KRIs) Defined

1. **Contractor Concentration Ratio (Top-10 Share):** Percentage of total multi-billion peso allocations awarded to the top 10 receiving contractors nationwide and per region.
2. **Regional/Provincial Cost Density:** Total provincial budget allocation and average project cost benchmarking across geographical regions.
3. **Regional Cost Z-Score ($Z_{\text{cost}}$):** Standardized statistical deviation of individual project costs relative to the regional mean:
   $$\text{Z-Score} = \frac{\text{Project Cost} - \mu_{\text{region}}}{\sigma_{\text{region}}}$$
4. **Coordinate Completeness Rate:** Percentage of project records containing valid, non-null GPS latitude and longitude coordinates for physical audit sampling.

---

## Target Data Schema Overview

The raw ingestion relies on public disclosures containing the following baseline entities:

* **Project Identification:** `ProjectId`, `ProjectName`
* **Administrative Hierarchy:** `Region`, `Province`, `DistrictEngineeringOffice`
* **Financials:** `ContractCost` (PHP)
* **Entities:** `Contractor`
* **Temporal & Spatial Meta:** `CompletionDate`, `Latitude`, `Longitude`

---

## ✅ Week 1 Definition of Done (DoD)

- [x] Core problem statement and project title finalized.
- [x] Target audience (COA Infrastructure Audit Division) and operational objective established.
- [x] Working audit hypotheses explicitly documented.
- [x] Primary public data sources identified (`bwandowando/dpwh-flood-control-projects`).
- [x] Project scope, analytical boundaries, and Key Risk Indicators (KRIs) defined.
- [x] Initial repository structure established (`docs/`, `data/raw/`, `data/processed/`, `scripts/`, `sql/`).
