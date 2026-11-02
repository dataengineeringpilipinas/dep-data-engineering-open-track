-- ============================================================
-- Gold Layer Relational Schema DDL — DPWH Flood Control
-- Target Engine: SQLite / DuckDB
-- File Path: sql/schema_ddl.sql
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- 1. Dimension Table: dim_location
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_location (
    location_id TEXT PRIMARY KEY,          -- PSGC Code
    province TEXT NOT NULL,
    region TEXT NOT NULL,
    population INTEGER,
    land_area_sqkm REAL
);

-- ------------------------------------------------------------
-- 2. Dimension Table: dim_contractor
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_contractor (
    contractor_id TEXT PRIMARY KEY,        -- Canonical Hash Key
    name_raw TEXT NOT NULL,                -- Original DPWH string
    name_clean TEXT NOT NULL,              -- Deduplicated Name
    is_consortium INTEGER DEFAULT 0 CHECK (is_consortium IN (0, 1)) -- Boolean
);

-- ------------------------------------------------------------
-- 3. Dimension Table: dim_implementing_office
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_implementing_office (
    office_id TEXT PRIMARY KEY,            -- Office Hash Key
    office_name TEXT NOT NULL,             -- e.g., Pampanga 1st DEO
    office_type TEXT NOT NULL              -- DEO or RO
);

-- ------------------------------------------------------------
-- 4. Fact Table: fact_flood_control_projects
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_flood_control_projects (
    project_id TEXT PRIMARY KEY,           -- Surrogate Hash Key
    contractor_id TEXT NOT NULL,
    location_id TEXT NOT NULL,
    office_id TEXT NOT NULL,
    completion_date TEXT,                  -- ISO-8601 Date (YYYY-MM-DD)
    contract_cost_php REAL NOT NULL CHECK (contract_cost_php >= 0),
    cost_zscore_regional REAL,
    FOREIGN KEY (contractor_id) REFERENCES dim_contractor(contractor_id) ON DELETE RESTRICT,
    FOREIGN KEY (location_id) REFERENCES dim_location(location_id) ON DELETE RESTRICT,
    FOREIGN KEY (office_id) REFERENCES dim_implementing_office(office_id) ON DELETE RESTRICT
);

-- ------------------------------------------------------------
-- 5. Performance Indexes
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_contractor ON fact_flood_control_projects(contractor_id);
CREATE INDEX IF NOT EXISTS idx_fact_location ON fact_flood_control_projects(location_id);
CREATE INDEX IF NOT EXISTS idx_fact_office ON fact_flood_control_projects(office_id);
