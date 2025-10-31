-- Stored procedure for validated crop yield record insert
-- Ensures state, crop, and season exist and values are within acceptable ranges
-- Validates yield calculation: yield should be approximately Production/Area

CREATE OR REPLACE FUNCTION sp_insert_crop_yield_record(
    p_state_name TEXT,
    p_crop_name TEXT,
    p_season_name TEXT,
    p_crop_year INTEGER,
    p_area NUMERIC,
    p_production NUMERIC,
    p_annual_rainfall NUMERIC,
    p_fertilizer NUMERIC,
    p_pesticide NUMERIC,
    p_yield NUMERIC
) RETURNS UUID AS $$
DECLARE
    v_state_id UUID;
    v_crop_id UUID;
    v_season_id UUID;
    v_new_id UUID;
    v_calculated_yield NUMERIC;
    v_yield_diff NUMERIC;
BEGIN
    -- Validate and get state_id
    SELECT state_id INTO v_state_id FROM states WHERE state_name = TRIM(p_state_name);
    IF v_state_id IS NULL THEN
        RAISE EXCEPTION 'State "%" does not exist', p_state_name USING ERRCODE = '23503';
    END IF;

    -- Validate and get crop_id
    SELECT crop_id INTO v_crop_id FROM crops WHERE crop_name = TRIM(p_crop_name);
    IF v_crop_id IS NULL THEN
        RAISE EXCEPTION 'Crop "%" does not exist', p_crop_name USING ERRCODE = '23503';
    END IF;

    -- Validate and get season_id
    SELECT season_id INTO v_season_id FROM seasons WHERE season_name = TRIM(p_season_name);
    IF v_season_id IS NULL THEN
        RAISE EXCEPTION 'Season "%" does not exist', p_season_name USING ERRCODE = '23503';
    END IF;

    -- Validate year range
    IF p_crop_year < 1990 OR p_crop_year > 2030 THEN
        RAISE EXCEPTION 'crop_year must be between 1990 and 2030';
    END IF;

    -- Validate non-negative values
    IF p_area < 0 THEN
        RAISE EXCEPTION 'area must be >= 0';
    END IF;
    IF p_production < 0 THEN
        RAISE EXCEPTION 'production must be >= 0';
    END IF;
    IF p_annual_rainfall < 0 THEN
        RAISE EXCEPTION 'annual_rainfall must be >= 0';
    END IF;
    IF p_fertilizer < 0 THEN
        RAISE EXCEPTION 'fertilizer must be >= 0';
    END IF;
    IF p_pesticide < 0 THEN
        RAISE EXCEPTION 'pesticide must be >= 0';
    END IF;
    IF p_yield < 0 THEN
        RAISE EXCEPTION 'yield must be >= 0';
    END IF;

    -- Validate yield calculation (allow 5% tolerance for rounding differences)
    IF p_area > 0 THEN
        v_calculated_yield := p_production / p_area;
        v_yield_diff := ABS(p_yield - v_calculated_yield) / NULLIF(v_calculated_yield, 0);
        IF v_yield_diff > 0.05 THEN
            RAISE WARNING 'Yield may not match Production/Area. Expected: %, Got: %', 
                v_calculated_yield, p_yield;
        END IF;
    END IF;

    -- Perform insert
    INSERT INTO crop_yield_records (
        state_id, crop_id, season_id, crop_year, area, production, 
        annual_rainfall, fertilizer, pesticide, yield
    ) VALUES (
        v_state_id, v_crop_id, v_season_id, p_crop_year, p_area, p_production,
        p_annual_rainfall, p_fertilizer, p_pesticide, p_yield
    ) RETURNING record_id INTO v_new_id;

    RETURN v_new_id;
END;
$$ LANGUAGE plpgsql;
