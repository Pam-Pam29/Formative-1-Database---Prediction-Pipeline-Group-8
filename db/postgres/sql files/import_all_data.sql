-- Complete import script - runs everything in one session
-- This avoids temp table session issues

-- ============================================
-- STEP 1: Create temporary table for CSV import
-- ============================================
CREATE TEMP TABLE IF NOT EXISTS temp_csv_import (
    Crop TEXT,
    Crop_Year INTEGER,
    Season TEXT,
    State TEXT,
    Area NUMERIC,
    Production NUMERIC,
    Annual_Rainfall NUMERIC,
    Fertilizer NUMERIC,
    Pesticide NUMERIC,
    Yield NUMERIC
);

-- ============================================
-- STEP 2: Load CSV into temporary table
-- ============================================
-- IMPORTANT: Update the path below to match your CSV file location
-- Use forward slashes / instead of backslashes \
COPY temp_csv_import FROM 'C:/Users/pampam/New folder (28)/Formative-1-Database---Prediction-Pipeline-Group-8/crop_yield.csv' 
    WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- ============================================
-- STEP 3: Populate lookup tables with unique values
-- ============================================

-- Import all unique states (trimming whitespace)
INSERT INTO states (state_name)
SELECT DISTINCT TRIM(State) 
FROM temp_csv_import
WHERE State IS NOT NULL
ON CONFLICT (state_name) DO NOTHING;

-- Import all unique crops (trimming whitespace)
INSERT INTO crops (crop_name)
SELECT DISTINCT TRIM(Crop) 
FROM temp_csv_import
WHERE Crop IS NOT NULL
ON CONFLICT (crop_name) DO NOTHING;

-- Import all unique seasons (trimming whitespace)
INSERT INTO seasons (season_name)
SELECT DISTINCT TRIM(Season) 
FROM temp_csv_import
WHERE Season IS NOT NULL
ON CONFLICT (season_name) DO NOTHING;

-- ============================================
-- STEP 4: Insert all records using stored procedure
-- ============================================
DO $$
DECLARE
    rec RECORD;
    v_count INTEGER := 0;
    v_errors INTEGER := 0;
BEGIN
    FOR rec IN 
        SELECT 
            TRIM(State) as state_name,
            TRIM(Crop) as crop_name,
            TRIM(Season) as season_name,
            Crop_Year,
            Area,
            Production,
            Annual_Rainfall,
            Fertilizer,
            Pesticide,
            Yield
        FROM temp_csv_import
    LOOP
        BEGIN
            PERFORM sp_insert_crop_yield_record(
                rec.state_name,
                rec.crop_name,
                rec.season_name,
                rec.Crop_Year,
                rec.Area,
                rec.Production,
                rec.Annual_Rainfall,
                rec.Fertilizer,
                rec.Pesticide,
                rec.Yield
            );
            v_count := v_count + 1;
            
            -- Progress indicator every 1000 records
            IF v_count % 1000 = 0 THEN
                RAISE NOTICE 'Inserted % records...', v_count;
            END IF;
        EXCEPTION WHEN OTHERS THEN
            v_errors := v_errors + 1;
            IF v_errors <= 10 THEN
                RAISE WARNING 'Error inserting record: State=%, Crop=%, Season=%, Year=% - %', 
                    rec.state_name, rec.crop_name, rec.season_name, rec.Crop_Year, SQLERRM;
            END IF;
        END;
    END LOOP;
    
    RAISE NOTICE 'Import complete! Inserted: %, Errors: %', v_count, v_errors;
END $$;

-- ============================================
-- VERIFICATION
-- ============================================
SELECT 'States' as table_name, COUNT(*) as count FROM states
UNION ALL
SELECT 'Crops', COUNT(*) FROM crops
UNION ALL
SELECT 'Seasons', COUNT(*) FROM seasons
UNION ALL
SELECT 'Crop Yield Records', COUNT(*) FROM crop_yield_records;

