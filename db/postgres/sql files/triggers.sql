-- Audit trigger for logging changes on crop_yield_records

CREATE OR REPLACE FUNCTION fn_audit_crop_yield_records() RETURNS TRIGGER AS $$
DECLARE
    v_old JSONB;
    v_new JSONB;
    v_row_pk UUID;
BEGIN
    IF (TG_OP = 'INSERT') THEN
        v_old := NULL;
        v_new := to_jsonb(NEW);
        v_row_pk := NEW.record_id;
    ELSIF (TG_OP = 'UPDATE') THEN
        v_old := to_jsonb(OLD);
        v_new := to_jsonb(NEW);
        v_row_pk := NEW.record_id;
    ELSIF (TG_OP = 'DELETE') THEN
        v_old := to_jsonb(OLD);
        v_new := NULL;
        v_row_pk := OLD.record_id;
    END IF;

    INSERT INTO audits (table_name, operation, row_pk, old_values, new_values)
    VALUES ('crop_yield_records', TG_OP, v_row_pk, v_old, v_new);

    -- For AFTER triggers, return NEW for INSERT/UPDATE, OLD for DELETE
    IF (TG_OP = 'DELETE') THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_crop_yield_records ON crop_yield_records;
CREATE TRIGGER trg_audit_crop_yield_records
AFTER INSERT OR UPDATE OR DELETE ON crop_yield_records
FOR EACH ROW EXECUTE FUNCTION fn_audit_crop_yield_records();
