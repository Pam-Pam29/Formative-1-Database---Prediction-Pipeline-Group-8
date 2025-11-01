// MongoDB Database Initialization Script

// Switch to or create the database
use agro_yield;

// --- STATES ---
const states = [
  { _id: 1, state_name: "Kigali" },
  { _id: 2, state_name: "Northern Province" },
  { _id: 3, state_name: "Eastern Province" }
];

states.forEach(s => {
  db.states.updateOne(
    { state_name: s.state_name },   
    { $setOnInsert: s },            
    { upsert: true }                
  );
});

// --- CROPS ---
const crops = [
  { _id: 1, crop_name: "Maize" },
  { _id: 2, crop_name: "Rice" },
  { _id: 3, crop_name: "Wheat" }
];

crops.forEach(c => {
  db.crops.updateOne(
    { crop_name: c.crop_name },
    { $setOnInsert: c },
    { upsert: true }
  );
});

// --- SEASONS ---
const seasons = [
  { _id: 1, season_name: "Dry Season" },
  { _id: 2, season_name: "Rainy Season" }
];

seasons.forEach(season => {
  db.seasons.updateOne(
    { season_name: season.season_name },
    { $setOnInsert: season },
    { upsert: true }
  );
});

// --- CROP_YIELD_RECORDS ---
const cropYieldRecords = [
  {
    _id: 1,
    state_id: 1,
    crop_id: 1,
    season_id: 2,
    year: 2024,
    area: 500,
    production: 1200
  },
  {
    _id: 2,
    state_id: 2,
    crop_id: 2,
    season_id: 1,
    year: 2024,
    area: 800,
    production: 2000
  }
];

cropYieldRecords.forEach(r => {
  db.crop_yield_records.updateOne(
    { _id: r._id },       
    { $setOnInsert: r },  
    { upsert: true }
  );
});

// --- AUDIT LOG (simulated by trigger)---
db.audit_log.updateOne(
  { message: "Initial crop yield data inserted successfully" },
  { $setOnInsert: { message: "Initial crop yield data inserted successfully", timestamp: new Date() } },
  { upsert: true }
);

print("✅ MongoDB setup completed. Existing data preserved, new records added if missing.");

// --- Example Aggregation-  ---
print("\n=== Sample Aggregation Result ===");
const results = db.crop_yield_records.aggregate([
  {
    $lookup: {
      from: "states",
      localField: "state_id",
      foreignField: "_id",
      as: "state"
    }
  },
  { $unwind: "$state" },
  {
    $lookup: {
      from: "crops",
      localField: "crop_id",
      foreignField: "_id",
      as: "crop"
    }
  },
  { $unwind: "$crop" },
  {
    $lookup: {
      from: "seasons",
      localField: "season_id",
      foreignField: "_id",
      as: "season"
    }
  },
  { $unwind: "$season" },
  {
    $project: {
      _id: 0,
      year: 1,
      area: 1,
      production: 1,
      "state.state_name": 1,
      "crop.crop_name": 1,
      "season.season_name": 1
    }
  }
]);

results.forEach(printjson);
