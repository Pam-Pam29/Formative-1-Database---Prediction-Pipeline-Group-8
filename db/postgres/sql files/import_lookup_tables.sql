-- Populate lookup tables with unique values from CSV
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

