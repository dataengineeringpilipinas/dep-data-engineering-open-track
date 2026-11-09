Week 7 — Relational Storage & Star Schema Design

**Project Title:** Public Data Patterns in DPWH Flood Control Projects (2022–2025)  
**Target Audience:** Commission on Audit (COA) — Infrastructure Audit Division  
**Document Path:** `docs/week07_storage_schema_design.md`  

---

## Executive Summary

Week 7 transitions the project storage design from a flat, unnormalized Bronze dataset (`data/raw/dpwh_flood_control_projects.csv`) into a structured **Star Schema Relational Model**. Storing records in a dimensional schema (Fact and Dimension tables) inside SQLite/DuckDB eliminates field redundancy, optimizes SQL analytical query execution, and enforces relational integrity across entities (contractors, locations, implementing offices).

---

## Star Schema Architecture

The relational storage model centers on a core fact table surrounded by three primary dimension tables:

```text
                  +--------------------------------+
                  |         dim_location           |
                  +--------------------------------+
                  | PK  location_id                |
                  |     province                   |
                  |     region                     |
                  +--------------------------------+
                                  │
                                  │ 1:N
                                  ▼
+-----------------------------------+     1:N     +-----------------------------------+
|      dim_implementing_office      |────────────►|    fact_flood_control_projects    |
+-----------------------------------+             +-----------------------------------+
| PK  office_id                     |             | PK  project_id                    |
|     district_engineering_office   |             | FK  contractor_id                 |
|     region                        |             | FK  location_id                   |
+-----------------------------------+             | FK  office_id                     |
                                                  |     contract_cost_php             |
                                  ▲               |     completion_date               |
                                  │ 1:N           |     cost_zscore_regional          |
                  +---------------+                |     latitude                      |
                  | dim_contractor|               |     longitude                     |
                  +---------------+               +-----------------------------------+
                  | PK  contractor_id             |
                  |     contractor_name           |
                  |     is_joint_venture          |
                  +-------------------------------+
