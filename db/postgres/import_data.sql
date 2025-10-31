-- Script to import crop_yield.csv data into the database
-- First, populate lookup tables with all unique values from CSV
-- Then use the stored procedure to insert records

-- Note: This script assumes you have loaded the CSV data into a temporary table
-- or are using COPY command or similar import method
-- Adjust the file path and import method based on your PostgreSQL setup

-- Example: Import unique states
INSERT INTO states (state_name)
SELECT DISTINCT TRIM(State) FROM (
    -- You would replace this with your CSV import method
    VALUES 
        ('Assam'),
        ('Karnataka'),
        ('Kerala')
    -- In practice, this would be: SELECT DISTINCT State FROM imported_csv_table
) AS temp(state)
ON CONFLICT (state_name) DO NOTHING;

-- Example: Import unique crops
INSERT INTO crops (crop_name)
SELECT DISTINCT TRIM(Crop) FROM (
    VALUES 
        ('Rice'),
        ('Wheat'),
        ('Maize')
    -- In practice: SELECT DISTINCT Crop FROM imported_csv_table
) AS temp(crop)
ON CONFLICT (crop_name) DO NOTHING;

-- Example: Import unique seasons
INSERT INTO seasons (season_name)
SELECT DISTINCT TRIM(Season) FROM (
    VALUES 
        ('Kharif'),
        ('Rabi'),
        ('Whole Year'),
        ('Autumn'),
        ('Summer'),
        ('Winter')
    -- In practice: SELECT DISTINCT Season FROM imported_csv_table
) AS temp(season)
ON CONFLICT (season_name) DO NOTHING;

-- Example: Insert a record using the stored procedure
-- CALL sp_insert_crop_yield_record(
--     'Assam',           -- state_name
--     'Rice',            -- crop_name
--     'Kharif',          -- season_name
--     1997,              -- crop_year
--     607358,            -- area
--     398311,            -- production
--     2051.4,            -- annual_rainfall
--     57802260.86,       -- fertilizer
--     188280.98,         -- pesticide
--     0.780869565        -- yield
-- );

