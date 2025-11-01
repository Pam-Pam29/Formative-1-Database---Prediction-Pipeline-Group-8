"""
MongoDB CRUD endpoints for crop yield records
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from bson import ObjectId
from bson.errors import InvalidId
from app.database import get_mongo_db
from app.models import (
    MongoCropYieldRecordCreate,
    MongoCropYieldRecordUpdate,
    MongoCropYieldRecordResponse
)
from datetime import datetime

router = APIRouter(prefix="/api/mongodb", tags=["MongoDB"])


def log_audit(operation: str, collection_name: str, document_id: str, changes: dict = None):
    """Log audit trail for MongoDB operations"""
    db = get_mongo_db()
    db.audit_log.insert_one({
        "operation": operation,
        "collection": collection_name,
        "document_id": document_id,
        "changes": changes,
        "timestamp": datetime.utcnow()
    })


@router.post("/records/", response_model=MongoCropYieldRecordResponse, status_code=201)
def create_record(record: MongoCropYieldRecordCreate):
    """
    Create a new crop yield record in MongoDB
    """
    try:
        db = get_mongo_db()
        
        state_doc = db.states.find_one({"state_name": record.state_name})
        if not state_doc:
            state_result = db.states.insert_one({"state_name": record.state_name})
            state_id = str(state_result.inserted_id)
        else:
            state_id = str(state_doc["_id"])
        
        crop_doc = db.crops.find_one({"crop_name": record.crop_name})
        if not crop_doc:
            crop_result = db.crops.insert_one({"crop_name": record.crop_name})
            crop_id = str(crop_result.inserted_id)
        else:
            crop_id = str(crop_doc["_id"])
        
        season_doc = db.seasons.find_one({"season_name": record.season_name})
        if not season_doc:
            season_result = db.seasons.insert_one({"season_name": record.season_name})
            season_id = str(season_result.inserted_id)
        else:
            season_id = str(season_doc["_id"])
        
        
        existing = db.crop_yield_records.find_one({
            "state_id": state_id,
            "crop_id": crop_id,
            "season_id": season_id,
            "year": record.year
        })
        
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Record already exists for this state, crop, season, and year combination"
            )
        
       
        record_doc = {
            "state_id": state_id,
            "crop_id": crop_id,
            "season_id": season_id,
            "year": record.year,
            "area": record.area,
            "production": record.production,
            "annual_rainfall": record.annual_rainfall,
            "fertilizer": record.fertilizer,
            "pesticide": record.pesticide,
            "yield": record.yield_value
        }
        
        
        result = db.crop_yield_records.insert_one(record_doc)
        inserted_id = str(result.inserted_id)
        
      
        log_audit("INSERT", "crop_yield_records", inserted_id, record_doc)
        
      
        created_doc = db.crop_yield_records.find_one({"_id": result.inserted_id})
        return MongoCropYieldRecordResponse(
            id=str(created_doc["_id"]),
            state_id=created_doc["state_id"],
            crop_id=created_doc["crop_id"],
            season_id=created_doc["season_id"],
            year=created_doc["year"],
            area=created_doc.get("area"),
            production=created_doc.get("production"),
            annual_rainfall=created_doc.get("annual_rainfall"),
            fertilizer=created_doc.get("fertilizer"),
            pesticide=created_doc.get("pesticide"),
            yield_value=created_doc.get("yield")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating record: {str(e)}")


@router.get("/records/", response_model=List[MongoCropYieldRecordResponse])
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
    try:
        db = get_mongo_db()
        
       
        filter_query = {}
        
        if state or crop or year:
            
            if state:
                state_docs = db.states.find({"state_name": {"$regex": state, "$options": "i"}})
                state_ids = [str(doc["_id"]) for doc in state_docs]
                if state_ids:
                    filter_query["state_id"] = {"$in": state_ids}
                else:
                    return []  
            
            if crop:
                crop_docs = db.crops.find({"crop_name": {"$regex": crop, "$options": "i"}})
                crop_ids = [str(doc["_id"]) for doc in crop_docs]
                if crop_ids:
                    filter_query["crop_id"] = {"$in": crop_ids}
                else:
                    return [] 
            
            if year:
                filter_query["year"] = year
        
        cursor = db.crop_yield_records.find(filter_query).sort("_id", -1).skip(offset).limit(limit)
        
        records = []
        for doc in cursor:
            records.append(MongoCropYieldRecordResponse(
                id=str(doc["_id"]),
                state_id=doc["state_id"],
                crop_id=doc["crop_id"],
                season_id=doc["season_id"],
                year=doc["year"],
                area=doc.get("area"),
                production=doc.get("production"),
                annual_rainfall=doc.get("annual_rainfall"),
                fertilizer=doc.get("fertilizer"),
                pesticide=doc.get("pesticide"),
                yield_value=doc.get("yield")
            ))
        
        return records
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching records: {str(e)}")


@router.get("/records/latest", response_model=MongoCropYieldRecordResponse)
def get_latest_record():
    """
    Get the most recent crop yield record
    """
    try:
        db = get_mongo_db()
        
        doc = db.crop_yield_records.find_one(sort=[("_id", -1)])
        
        if not doc:
            raise HTTPException(status_code=404, detail="No records found")
        
        return MongoCropYieldRecordResponse(
            id=str(doc["_id"]),
            state_id=doc["state_id"],
            crop_id=doc["crop_id"],
            season_id=doc["season_id"],
            year=doc["year"],
            area=doc.get("area"),
            production=doc.get("production"),
            annual_rainfall=doc.get("annual_rainfall"),
            fertilizer=doc.get("fertilizer"),
            pesticide=doc.get("pesticide"),
            yield_value=doc.get("yield")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching latest record: {str(e)}")


@router.get("/records/{record_id}", response_model=MongoCropYieldRecordResponse)
def get_record(record_id: str):
    """
    Get a specific crop yield record by ID
    """
    try:
        db = get_mongo_db()
        
        try:
            obj_id = ObjectId(record_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail=f"Invalid record ID: {record_id}")
        
        doc = db.crop_yield_records.find_one({"_id": obj_id})
        
        if not doc:
            raise HTTPException(status_code=404, detail=f"Record with ID {record_id} not found")
        
        return MongoCropYieldRecordResponse(
            id=str(doc["_id"]),
            state_id=doc["state_id"],
            crop_id=doc["crop_id"],
            season_id=doc["season_id"],
            year=doc["year"],
            area=doc.get("area"),
            production=doc.get("production"),
            annual_rainfall=doc.get("annual_rainfall"),
            fertilizer=doc.get("fertilizer"),
            pesticide=doc.get("pesticide"),
            yield_value=doc.get("yield")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching record: {str(e)}")


@router.put("/records/{record_id}", response_model=MongoCropYieldRecordResponse)
def update_record(record_id: str, record_update: MongoCropYieldRecordUpdate):
    """
    Update an existing crop yield record
    """
    try:
        db = get_mongo_db()
        
        try:
            obj_id = ObjectId(record_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail=f"Invalid record ID: {record_id}")
        
        existing_doc = db.crop_yield_records.find_one({"_id": obj_id})
        if not existing_doc:
            raise HTTPException(status_code=404, detail=f"Record with ID {record_id} not found")
        
        update_doc = {}
        
        if record_update.state_name:
            state_doc = db.states.find_one({"state_name": record_update.state_name})
            if not state_doc:
                state_result = db.states.insert_one({"state_name": record_update.state_name})
                update_doc["state_id"] = str(state_result.inserted_id)
            else:
                update_doc["state_id"] = str(state_doc["_id"])
        
        if record_update.crop_name:
            crop_doc = db.crops.find_one({"crop_name": record_update.crop_name})
            if not crop_doc:
                crop_result = db.crops.insert_one({"crop_name": record_update.crop_name})
                update_doc["crop_id"] = str(crop_result.inserted_id)
            else:
                update_doc["crop_id"] = str(crop_doc["_id"])
        
        if record_update.season_name:
            season_doc = db.seasons.find_one({"season_name": record_update.season_name})
            if not season_doc:
                season_result = db.seasons.insert_one({"season_name": record_update.season_name})
                update_doc["season_id"] = str(season_result.inserted_id)
            else:
                update_doc["season_id"] = str(season_doc["_id"])
        
        if record_update.year is not None:
            update_doc["year"] = record_update.year
        
        if record_update.area is not None:
            update_doc["area"] = record_update.area
        
        if record_update.production is not None:
            update_doc["production"] = record_update.production
        
        if record_update.annual_rainfall is not None:
            update_doc["annual_rainfall"] = record_update.annual_rainfall
        
        if record_update.fertilizer is not None:
            update_doc["fertilizer"] = record_update.fertilizer
        
        if record_update.pesticide is not None:
            update_doc["pesticide"] = record_update.pesticide
        
        if record_update.yield_value is not None:
            update_doc["yield"] = record_update.yield_value
        
        if not update_doc:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        
        state_id = update_doc.get("state_id", existing_doc["state_id"])
        crop_id = update_doc.get("crop_id", existing_doc["crop_id"])
        season_id = update_doc.get("season_id", existing_doc["season_id"])
        year = update_doc.get("year", existing_doc["year"])
        
        duplicate = db.crop_yield_records.find_one({
            "state_id": state_id,
            "crop_id": crop_id,
            "season_id": season_id,
            "year": year,
            "_id": {"$ne": obj_id}
        })
        
        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="Update would create a duplicate record"
            )
        
        result = db.crop_yield_records.update_one(
            {"_id": obj_id},
            {"$set": update_doc}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail=f"Record with ID {record_id} not found")
        
        log_audit("UPDATE", "crop_yield_records", record_id, update_doc)
        
        updated_doc = db.crop_yield_records.find_one({"_id": obj_id})
        return MongoCropYieldRecordResponse(
            id=str(updated_doc["_id"]),
            state_id=updated_doc["state_id"],
            crop_id=updated_doc["crop_id"],
            season_id=updated_doc["season_id"],
            year=updated_doc["year"],
            area=updated_doc.get("area"),
            production=updated_doc.get("production"),
            annual_rainfall=updated_doc.get("annual_rainfall"),
            fertilizer=updated_doc.get("fertilizer"),
            pesticide=updated_doc.get("pesticide"),
            yield_value=updated_doc.get("yield")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating record: {str(e)}")


@router.delete("/records/{record_id}", status_code=204)
def delete_record(record_id: str):
    """
    Delete a crop yield record by ID
    """
    try:
        db = get_mongo_db()
        
        try:
            obj_id = ObjectId(record_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail=f"Invalid record ID: {record_id}")
        
        doc = db.crop_yield_records.find_one({"_id": obj_id})
        if not doc:
            raise HTTPException(status_code=404, detail=f"Record with ID {record_id} not found")
        
        result = db.crop_yield_records.delete_one({"_id": obj_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Record with ID {record_id} not found")
        
        log_audit("DELETE", "crop_yield_records", record_id, dict(doc))
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting record: {str(e)}")
