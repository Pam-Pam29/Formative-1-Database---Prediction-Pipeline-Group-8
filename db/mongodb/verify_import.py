"""
Verification script for MongoDB crop yield import
Checks collection counts, references, duplicates, and audit logs
"""

from pymongo import MongoClient
from pathlib import Path
import os

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.agro_yield

def collection_counts():
    print("="*60)
    print("COLLECTION COUNTS")
    print("="*60)
    collections = ["states", "crops", "seasons", "crop_yield_records", "audit_log"]
    for col in collections:
        count = db[col].count_documents({})
        print(f"  {col:20} : {count:,}")
    print("")

def check_lookup_references():
    print("="*60)
    print("LOOKUP TABLE REFERENCES")
    print("="*60)
    state_ids = set(doc["_id"] for doc in db.states.find({}, {"_id": 1}))
    crop_ids = set(doc["_id"] for doc in db.crops.find({}, {"_id": 1}))
    season_ids = set(doc["_id"] for doc in db.seasons.find({}, {"_id": 1}))

    missing_state = db.crop_yield_records.count_documents({"state_id": {"$nin": list(state_ids)}})
    missing_crop = db.crop_yield_records.count_documents({"crop_id": {"$nin": list(crop_ids)}})
    missing_season = db.crop_yield_records.count_documents({"season_id": {"$nin": list(season_ids)}})

    print(f"  Records with missing state_id  : {missing_state}")
    print(f"  Records with missing crop_id   : {missing_crop}")
    print(f"  Records with missing season_id : {missing_season}")
    print("")

def check_duplicates():
    print("="*60)
    print("CHECK DUPLICATES IN FACT TABLE")
    print("="*60)
    pipeline = [
        {"$group": {
            "_id": {"state_id": "$state_id", "crop_id": "$crop_id", "season_id": "$season_id", "year": "$year"},
            "count": {"$sum": 1}
        }},
        {"$match": {"count": {"$gt": 1}}}
    ]
    duplicates = list(db.crop_yield_records.aggregate(pipeline))
    if duplicates:
        print(f"  [WARN] Found {len(duplicates)} duplicate combinations in crop_yield_records!")
        for dup in duplicates[:5]:  # show first 5
            print(f"    {dup['_id']} -> {dup['count']} times")
    else:
        print("  [OK] No duplicates found")
    print("")

def check_audit_log():
    print("="*60)
    print("AUDIT LOG SUMMARY")
    print("="*60)
    total_audits = db.audit_log.count_documents({})
    inserts = db.audit_log.count_documents({"operation": "INSERT"})
    updates = db.audit_log.count_documents({"operation": "UPDATE"})
    deletes = db.audit_log.count_documents({"operation": "DELETE"})
    
    print(f"  Total audit entries : {total_audits:,}")
    print(f"  Inserts logged      : {inserts:,}")
    print(f"  Updates logged      : {updates:,}")
    print(f"  Deletes logged      : {deletes:,}")
    print("")

def main():
    print("\nVERIFICATION OF MONGODB IMPORT")
    print("="*60)
    collection_counts()
    check_lookup_references()
    check_duplicates()
    check_audit_log()
    print("="*60)
    print("VERIFICATION COMPLETE\n")

if __name__ == "__main__":
    main()
