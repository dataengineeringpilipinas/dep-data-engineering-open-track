-- ============================================================
-- Phase 3 — Milestone 3 (Week 8): SQL Business Queries
-- Public Data Patterns in DPWH Flood Control Projects (2022–2025)
-- ============================================================

-- Table: projects_cleaned = data/processed/dpwh_flood_control_projects_cleaned.csv
-- Run all three: python scripts/run_sql_queries.py
-- Note: rows with no numeric cost (multi-year contract continuation rows) are
-- ignored by SUM and AVG, and COUNT(DISTINCT project_id) counts each project once.

-- ------------------------------------------------------------
-- QUESTION 1
-- Which top 10 contractors received the largest total contract
-- value for DPWH flood control projects between 2022 and 2025?
-- ------------------------------------------------------------

SELECT
    contractor AS contractor_name,
    COUNT(DISTINCT project_id) AS total_projects_awarded,
    ROUND(SUM(contract_cost_php), 2) AS total_contract_value_php,
    ROUND(AVG(contract_cost_php), 2) AS avg_project_cost_php
FROM projects_cleaned
WHERE contractor IS NOT NULL
  AND contractor != ''
GROUP BY
    contractor
ORDER BY
    total_contract_value_php DESC,
    contractor
LIMIT 10;


-- ------------------------------------------------------------
-- QUESTION 2
-- Which provinces received the highest total flood control
-- funding and project volume between 2022 and 2025?
-- ------------------------------------------------------------

SELECT
    province AS province,
    region AS region,
    COUNT(DISTINCT project_id) AS total_projects,
    ROUND(SUM(contract_cost_php), 2) AS total_provincial_funding_php,
    ROUND(AVG(contract_cost_php), 2) AS avg_project_cost_php
FROM projects_cleaned
WHERE province IS NOT NULL
  AND province != ''
GROUP BY
    province,
    region
ORDER BY
    total_provincial_funding_php DESC,
    province
LIMIT 15;


-- ------------------------------------------------------------
-- QUESTION 3
-- Which District Engineering Offices (DEOs) manage projects with
-- the highest average contract costs (minimum 10 projects managed)?
-- ------------------------------------------------------------

SELECT
    district_engineering_office AS implementing_office,
    COUNT(DISTINCT project_id) AS total_projects_managed,
    ROUND(SUM(contract_cost_php), 2) AS total_budget_managed_php,
    ROUND(AVG(contract_cost_php), 2) AS avg_contract_cost_php
FROM projects_cleaned
WHERE district_engineering_office IS NOT NULL
  AND district_engineering_office != ''
GROUP BY
    district_engineering_office
HAVING
    COUNT(DISTINCT project_id) >= 10
ORDER BY
    avg_contract_cost_php DESC,
    district_engineering_office
LIMIT 10;