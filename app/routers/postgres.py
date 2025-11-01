"""
PostgreSQL CRUD endpoints for crop yield records
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from uuid import UUID
from app.database import get_postgres_conn, return_postgres_conn
from app.models import (
    CropYieldRecordCreate,
    CropYieldRecordUpdate,
    CropYieldRecordResponse
)
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/postgres", tags=["PostgreSQL"])


@router.post("/records/", response_model=CropYieldRecordResponse, status_code=201)
def create_record(record: CropYieldRecordCreate):
    """
    Create a new crop yield record using the stored procedure
    """
    conn = None
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
       
        cursor.execute("""
            SELECT sp_insert_crop_yield_record(
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) AS record_id
        """, [
            record.state_name,
            record.crop_name,
            record.season_name,
            record.crop_year,
            record.area,
            record.production,
            record.annual_rainfall,
            record.fertilizer,
            record.pesticide,
            record.yield_value
        ])
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=500, detail="Failed to get record ID from stored procedure")
        
        
        record_id = result['record_id']
        conn.commit()
        
       
        cursor.execute("""
            SELECT 
                cyr.record_id,
                s.state_name,
                c.crop_name,
                se.season_name,
                cyr.crop_year,
                cyr.area,
                cyr.production,
                cyr.annual_rainfall,
                cyr.fertilizer,
                cyr.pesticide,
                cyr.yield as yield_value,
                cyr.created_at
            FROM crop_yield_records cyr
            JOIN states s ON cyr.state_id = s.state_id
            JOIN crops c ON cyr.crop_id = c.crop_id
            JOIN seasons se ON cyr.season_id = se.season_id
            WHERE cyr.record_id = %s
        """, (str(record_id),))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Record not found after creation")
        
        return CropYieldRecordResponse(**dict(result))
        
    except psycopg2.errors.UniqueViolation:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="Record already exists for this state, crop, season, and year combination"
        )
    except psycopg2.errors.IntegrityError as e:
        if conn:
            conn.rollback()
        logger.error(f"Integrity error creating record: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"PostgreSQL error creating record: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error creating record: {type(e).__name__}: {e}", exc_info=True)
        error_detail = str(e) if str(e) else f"{type(e).__name__}: {repr(e)}"
        raise HTTPException(status_code=500, detail=f"Error creating record: {error_detail}")
    finally:
        if conn:
            cursor.close()
            return_postgres_conn(conn)


@router.get("/records/", response_model=List[CropYieldRecordResponse])
def list_records(
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    state: Optional[str] = Query(None, description="Filter by state name"),
    crop: Optional[str] = Query(None, description="Filter by crop name"),
    year: Optional[int] = Query(None, ge=1990, le=2030, description="Filter by crop year")
):
    """
    List crop yield records with optional filtering and pagination
    """
    conn = None
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        
        query = """
            SELECT 
                cyr.record_id,
                s.state_name,
                c.crop_name,
                se.season_name,
                cyr.crop_year,
                cyr.area,
                cyr.production,
                cyr.annual_rainfall,
                cyr.fertilizer,
                cyr.pesticide,
                cyr.yield as yield_value,
                cyr.created_at
            FROM crop_yield_records cyr
            JOIN states s ON cyr.state_id = s.state_id
            JOIN crops c ON cyr.crop_id = c.crop_id
            JOIN seasons se ON cyr.season_id = se.season_id
            WHERE 1=1
        """
        params = []
        
        if state:
            query += " AND s.state_name ILIKE %s"
            params.append(f"%{state}%")
        
        if crop:
            query += " AND c.crop_name ILIKE %s"
            params.append(f"%{crop}%")
        
        if year:
            query += " AND cyr.crop_year = %s"
            params.append(year)
        
        query += " ORDER BY cyr.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return [CropYieldRecordResponse(**dict(row)) for row in results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching records: {str(e)}")
    finally:
        if conn:
            cursor.close()
            return_postgres_conn(conn)


@router.get("/records/latest", response_model=CropYieldRecordResponse)
def get_latest_record():
    """
    Get the most recent crop yield record
    """
    conn = None
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                cyr.record_id,
                s.state_name,
                c.crop_name,
                se.season_name,
                cyr.crop_year,
                cyr.area,
                cyr.production,
                cyr.annual_rainfall,
                cyr.fertilizer,
                cyr.pesticide,
                cyr.yield as yield_value,
                cyr.created_at
            FROM crop_yield_records cyr
            JOIN states s ON cyr.state_id = s.state_id
            JOIN crops c ON cyr.crop_id = c.crop_id
            JOIN seasons se ON cyr.season_id = se.season_id
            ORDER BY cyr.created_at DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="No records found")
        
        return CropYieldRecordResponse(**dict(result))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching latest record: {str(e)}")
    finally:
        if conn:
            cursor.close()
            return_postgres_conn(conn)


@router.get("/records/{record_id}", response_model=CropYieldRecordResponse)
def get_record(record_id: UUID):
    """
    Get a specific crop yield record by ID
    """
    conn = None
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                cyr.record_id,
                s.state_name,
                c.crop_name,
                se.season_name,
                cyr.crop_year,
                cyr.area,
                cyr.production,
                cyr.annual_rainfall,
                cyr.fertilizer,
                cyr.pesticide,
                cyr.yield as yield_value,
                cyr.created_at
            FROM crop_yield_records cyr
            JOIN states s ON cyr.state_id = s.state_id
            JOIN crops c ON cyr.crop_id = c.crop_id
            JOIN seasons se ON cyr.season_id = se.season_id
            WHERE cyr.record_id = %s
        """, (str(record_id),))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail=f"Record with ID {record_id} not found")
        
        return CropYieldRecordResponse(**dict(result))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching record: {str(e)}")
    finally:
        if conn:
            cursor.close()
            return_postgres_conn(conn)


@router.put("/records/{record_id}", response_model=CropYieldRecordResponse)
def update_record(record_id: UUID, record_update: CropYieldRecordUpdate):
    """
    Update an existing crop yield record
    """
    conn = None
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
      
        cursor.execute("SELECT record_id FROM crop_yield_records WHERE record_id = %s", (str(record_id),))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Record with ID {record_id} not found")
        
       
        update_fields = []
        params = []
        
        if record_update.state_name:
           
            cursor.execute("SELECT state_id FROM states WHERE state_name = %s", (record_update.state_name,))
            state_result = cursor.fetchone()
            if not state_result:
                raise HTTPException(status_code=400, detail=f"State '{record_update.state_name}' does not exist")
            update_fields.append("state_id = %s")
            params.append(str(state_result['state_id']))
        
        if record_update.crop_name:
            cursor.execute("SELECT crop_id FROM crops WHERE crop_name = %s", (record_update.crop_name,))
            crop_result = cursor.fetchone()
            if not crop_result:
                raise HTTPException(status_code=400, detail=f"Crop '{record_update.crop_name}' does not exist")
            update_fields.append("crop_id = %s")
            params.append(str(crop_result['crop_id']))
        
        if record_update.season_name:
            cursor.execute("SELECT season_id FROM seasons WHERE season_name = %s", (record_update.season_name,))
            season_result = cursor.fetchone()
            if not season_result:
                raise HTTPException(status_code=400, detail=f"Season '{record_update.season_name}' does not exist")
            update_fields.append("season_id = %s")
            params.append(str(season_result['season_id']))
        
        if record_update.crop_year is not None:
            update_fields.append("crop_year = %s")
            params.append(record_update.crop_year)
        
        if record_update.area is not None:
            update_fields.append("area = %s")
            params.append(record_update.area)
        
        if record_update.production is not None:
            update_fields.append("production = %s")
            params.append(record_update.production)
        
        if record_update.annual_rainfall is not None:
            update_fields.append("annual_rainfall = %s")
            params.append(record_update.annual_rainfall)
        
        if record_update.fertilizer is not None:
            update_fields.append("fertilizer = %s")
            params.append(record_update.fertilizer)
        
        if record_update.pesticide is not None:
            update_fields.append("pesticide = %s")
            params.append(record_update.pesticide)
        
        if record_update.yield_value is not None:
            update_fields.append("yield = %s")
            params.append(record_update.yield_value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        
        update_query = f"UPDATE crop_yield_records SET {', '.join(update_fields)} WHERE record_id = %s"
        params.append(str(record_id))
        
        logger.info(f"Update query: {update_query}")
        logger.info(f"Update params count: {len(params)}")
        logger.info(f"Record ID: {record_id}")
        logger.info(f"Params types: {[type(p).__name__ for p in params]}")
        
        try:
            cursor.execute(update_query, params)
        except Exception as query_error:
            logger.error(f"Error executing update query: {query_error}", exc_info=True)
            logger.error(f"Query: {update_query}")
            logger.error(f"Params types: {[type(p).__name__ for p in params]}")
            raise
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Record with ID {record_id} not found")
        
        conn.commit()
        
        cursor.execute("""
            SELECT 
                cyr.record_id,
                s.state_name,
                c.crop_name,
                se.season_name,
                cyr.crop_year,
                cyr.area,
                cyr.production,
                cyr.annual_rainfall,
                cyr.fertilizer,
                cyr.pesticide,
                cyr.yield as yield_value,
                cyr.created_at
            FROM crop_yield_records cyr
            JOIN states s ON cyr.state_id = s.state_id
            JOIN crops c ON cyr.crop_id = c.crop_id
            JOIN seasons se ON cyr.season_id = se.season_id
            WHERE cyr.record_id = %s
        """, (str(record_id),))
        
        result = cursor.fetchone()
        return CropYieldRecordResponse(**dict(result))
        
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="Update would create a duplicate record"
        )
    except psycopg2.errors.IntegrityError as e:
        conn.rollback()
        logger.error(f"Integrity error updating record {record_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Database integrity error: {str(e)}")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"PostgreSQL error updating record {record_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error updating record {record_id}: {type(e).__name__}: {e}", exc_info=True)
        error_detail = str(e) if str(e) else f"{type(e).__name__}: {repr(e)}"
        raise HTTPException(status_code=500, detail=f"Error updating record: {error_detail}")
    finally:
        if conn:
            cursor.close()
            return_postgres_conn(conn)


@router.delete("/records/{record_id}", status_code=204)
def delete_record(record_id: UUID):
    """
    Delete a crop yield record by ID
    """
    conn = None
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT record_id FROM crop_yield_records WHERE record_id = %s", (str(record_id),))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Record with ID {record_id} not found")
        
        cursor.execute("DELETE FROM crop_yield_records WHERE record_id = %s", (str(record_id),))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Record with ID {record_id} not found")
        
        conn.commit()
        return None
        
    except HTTPException:
        raise
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete record: referenced by other records"
        )
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting record: {str(e)}")
    finally:
        if conn:
            cursor.close()
            return_postgres_conn(conn)
