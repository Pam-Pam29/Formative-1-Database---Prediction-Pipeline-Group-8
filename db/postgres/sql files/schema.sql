-- PostgreSQL schema for AgroYield Task 1
-- Based on Indian States Crop Yield Dataset (1997-2020)
-- Schema normalized to 3NF with: states, crops, seasons, crop_yield_records, audits

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1) Lookup: states (Indian states/union territories)
CREATE TABLE IF NOT EXISTS states (
    state_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    state_name TEXT NOT NULL UNIQUE
);

-- 2) Lookup: crops (crop types)
CREATE TABLE IF NOT EXISTS crops (
    crop_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_name TEXT NOT NULL UNIQUE
);

-- 3) Lookup: seasons (Kharif, Rabi, Whole Year, Autumn, Summer, Winter)
CREATE TABLE IF NOT EXISTS seasons (
    season_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    season_name TEXT NOT NULL UNIQUE
);

-- 4) Fact table: crop_yield_records (main data table)
CREATE TABLE IF NOT EXISTS crop_yield_records (
    record_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    state_id UUID NOT NULL REFERENCES states(state_id) ON DELETE RESTRICT,
    crop_id UUID NOT NULL REFERENCES crops(crop_id) ON DELETE RESTRICT,
    season_id UUID NOT NULL REFERENCES seasons(season_id) ON DELETE RESTRICT,
    crop_year INTEGER NOT NULL CHECK (crop_year >= 1990 AND crop_year <= 2030),
    area NUMERIC(12,2) NOT NULL CHECK (area >= 0),
    production NUMERIC(15,2) NOT NULL CHECK (production >= 0),
    annual_rainfall NUMERIC(10,2) NOT NULL CHECK (annual_rainfall >= 0),
    fertilizer NUMERIC(15,2) NOT NULL CHECK (fertilizer >= 0),
    pesticide NUMERIC(12,2) NOT NULL CHECK (pesticide >= 0),
    yield NUMERIC(15,4) NOT NULL CHECK (yield >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(state_id, crop_id, season_id, crop_year)
);

-- 5) Audit table for triggers
CREATE TABLE IF NOT EXISTS audits (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    row_pk UUID NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changed_by TEXT DEFAULT current_user,
    old_values JSONB,
    new_values JSONB
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_yield_records_state ON crop_yield_records(state_id);
CREATE INDEX IF NOT EXISTS idx_yield_records_crop ON crop_yield_records(crop_id);
CREATE INDEX IF NOT EXISTS idx_yield_records_season ON crop_yield_records(season_id);
CREATE INDEX IF NOT EXISTS idx_yield_records_year ON crop_yield_records(crop_year);
CREATE INDEX IF NOT EXISTS idx_yield_records_year_crop ON crop_yield_records(crop_year, crop_id);
CREATE INDEX IF NOT EXISTS idx_audits_table_time ON audits(table_name, changed_at DESC);

-- Minimal seed data (safe to re-run)
INSERT INTO states (state_name) VALUES 
    ('Assam'), ('Karnataka'), ('Kerala')
ON CONFLICT (state_name) DO NOTHING;

INSERT INTO crops (crop_name) VALUES 
    ('Rice'), ('Wheat'), ('Maize')
ON CONFLICT (crop_name) DO NOTHING;

INSERT INTO seasons (season_name) VALUES 
    ('Kharif'), ('Rabi'), ('Whole Year')
ON CONFLICT (season_name) DO NOTHING;
