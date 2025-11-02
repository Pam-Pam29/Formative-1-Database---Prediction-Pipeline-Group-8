import pandas as pd
from pymongo import MongoClient, UpdateOne
from pathlib import Path
import os
from datetime import datetime
import requests

CSV_FILE = Path(__file__).parent / "crop_yield.csv"

# Download CSV if it doesn't exist
if not CSV_FILE.exists():
    url = "https://raw.githubusercontent.com/Pam-Pam29/Formative-1-Database---Prediction-Pipeline-Group-8/main/db/postgres/crop_yield.csv"
    r = requests.get(url)
    CSV_FILE.write_bytes(r.content)


# MongoDB connection
MONGO_URI = "mongodb+srv://<username>:<password>@cluster0.xxxxxx.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client.agroyeild

#Audit Logging
def log_audit(operation, collection_name, document_id, changes=None):
    """Insert an audit log entry"""
    db.audit_log.insert_one({
        "operation": operation,           
        "collection": collection_name,
        "document_id": document_id,
        "changes": changes,               
        "timestamp": datetime.utcnow()
    })

#Lookup Helpers
def import_lookup(collection_name, field_name, values):
    """Upsert lookup values into collection"""
    operations = [UpdateOne({field_name: v}, {"$setOnInsert": {field_name: v}}, upsert=True) for v in values]
    if operations:
        db[collection_name].bulk_write(operations)

def get_lookup_ids(collection_name, field_name):
    """Return dict of value -> _id"""
    return {doc[field_name]: doc["_id"] for doc in db[collection_name].find({}, {"_id": 1, field_name: 1})}

#CRUD Operations
def insert_crop_yield(record):
    """Insert record and log audit"""
    inserted_id = db.crop_yield_records.insert_one(record).inserted_id
    log_audit("INSERT", "crop_yield_records", inserted_id, changes=record)
    return inserted_id

def update_crop_yield(filter_query, updates):
    """Update record and log audit"""
    old_doc = db.crop_yield_records.find_one(filter_query)
    if not old_doc:
        return None
    result = db.crop_yield_records.update_one(filter_query, {"$set": updates})
    log_audit("UPDATE", "crop_yield_records", old_doc["_id"], changes=updates)
    return result.modified_count

def delete_crop_yield(filter_query):
    """Delete record and log audit"""
    doc = db.crop_yield_records.find_one(filter_query)
    if not doc:
        return None
    result = db.crop_yield_records.delete_one(filter_query)
    log_audit("DELETE", "crop_yield_records", doc["_id"], changes=doc)
    return result.deleted_count

# Import CSV 
def import_csv():
    df = pd.read_csv(CSV_FILE)
    df = df.dropna(subset=["State", "Crop", "Season", "Crop_Year"])
    
    # Upsert lookup tables
    import_lookup("states", "state_name", df["State"].str.strip().unique())
    import_lookup("crops", "crop_name", df["Crop"].str.strip().unique())
    import_lookup("seasons", "season_name", df["Season"].str.strip().unique())
    
    # Get lookup IDs
    state_ids = get_lookup_ids("states", "state_name")
    crop_ids = get_lookup_ids("crops", "crop_name")
    season_ids = get_lookup_ids("seasons", "season_name")
    
    # Insert or update crop yield records
    count_inserted = 0
    count_updated = 0
    for _, row in df.iterrows():
        state_id = state_ids[row["State"].strip()]
        crop_id = crop_ids[row["Crop"].strip()]
        season_id = season_ids[row["Season"].strip()]
        year = int(row["Crop_Year"])

        record_data = {
            "state_id": state_id,
            "crop_id": crop_id,
            "season_id": season_id,
            "year": year,
            "area": float(row["Area"]) if pd.notna(row["Area"]) else None,
            "production": float(row["Production"]) if pd.notna(row["Production"]) else None,
            "annual_rainfall": float(row["Annual_Rainfall"]) if pd.notna(row["Annual_Rainfall"]) else None,
            "fertilizer": float(row["Fertilizer"]) if pd.notna(row["Fertilizer"]) else None,
            "pesticide": float(row["Pesticide"]) if pd.notna(row["Pesticide"]) else None,
            "yield": float(row["Yield"]) if pd.notna(row["Yield"]) else None
        }

        # Check if record exists
        existing = db.crop_yield_records.find_one({
            "state_id": state_id,
            "crop_id": crop_id,
            "season_id": season_id,
            "year": year
        })
        if existing:
            # update if values changed
            updates = {k: v for k, v in record_data.items() if existing.get(k) != v}
            if updates:
                update_crop_yield({"_id": existing["_id"]}, updates)
                count_updated += 1
        else:
            insert_crop_yield(record_data)
            count_inserted += 1

    print(f"✅ Imported {count_inserted} new records, updated {count_updated} existing records.")

if __name__ == "__main__":
    import_csv()

