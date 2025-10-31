-- Insert all records using stored procedure
-- This will take some time for ~19,690 records

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
            RAISE WARNING 'Error inserting record: State=%, Crop=%, Season=%, Year=% - %', 
                rec.state_name, rec.crop_name, rec.season_name, rec.Crop_Year, SQLERRM;
        END;
    END LOOP;
    
    RAISE NOTICE 'Import complete! Inserted: %, Errors: %', v_count, v_errors;
END $$;

