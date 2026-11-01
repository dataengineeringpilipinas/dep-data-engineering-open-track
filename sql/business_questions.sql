-- ============================================================
-- Phase 3 — Milestone 2: SQL Business Queries
-- Public Data Patterns in DPWH Flood Control Projects (2022–2025)
-- ============================================================


-- ------------------------------------------------------------
-- QUESTION 1
-- Which top 10 contractors received the largest total contract
-- value for DPWH flood control projects between 2022 and 2025?
-- ------------------------------------------------------------

SELECT
    Contractor AS contractor_name,
    COUNT(ProjectId) AS total_projects_awarded,
    ROUND(SUM(ContractCost), 2) AS total_contract_value_php,
    ROUND(AVG(ContractCost), 2) AS avg_project_cost_php
FROM dpwh_flood_control_projects
WHERE Contractor IS NOT NULL
  AND Contractor != ''
GROUP BY
    Contractor
ORDER BY
    total_contract_value_php DESC,
    Contractor
LIMIT 10;


-- ------------------------------------------------------------
-- QUESTION 2
-- Which provinces received the highest total flood control
-- funding and project volume between 2022 and 2025?
-- ------------------------------------------------------------

SELECT
    Province AS province,
    Region AS region,
    COUNT(ProjectId) AS total_projects,
    ROUND(SUM(ContractCost), 2) AS total_provincial_funding_php,
    ROUND(AVG(ContractCost), 2) AS avg_project_cost_php
FROM dpwh_flood_control_projects
WHERE Province IS NOT NULL
  AND Province != ''
GROUP BY
    Province,
    Region
ORDER BY
    total_provincial_funding_php DESC,
    Province
LIMIT 15;


-- ------------------------------------------------------------
-- QUESTION 3
-- Which District Engineering Offices (DEOs) manage projects with
-- the highest average contract costs (minimum 10 projects managed)?
-- ------------------------------------------------------------

SELECT
    DistrictEngineeringOffice AS implementing_office,
    COUNT(ProjectId) AS total_projects_managed,
    ROUND(SUM(ContractCost), 2) AS total_budget_managed_php,
    ROUND(AVG(ContractCost), 2) AS avg_contract_cost_php
FROM dpwh_flood_control_projects
WHERE DistrictEngineeringOffice IS NOT NULL
  AND DistrictEngineeringOffice != ''
GROUP BY
    DistrictEngineeringOffice
HAVING
    COUNT(ProjectId) >= 10
ORDER BY
    avg_contract_cost_php DESC,
    DistrictEngineeringOffice
LIMIT 10;