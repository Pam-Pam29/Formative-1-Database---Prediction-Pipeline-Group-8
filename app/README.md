# AgroYield FastAPI Application

FastAPI application providing CRUD endpoints for crop yield records in both PostgreSQL and MongoDB.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Run the application:
```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### PostgreSQL Endpoints

#### Create Record
- **POST** `/api/postgres/records/`
- Creates a new crop yield record using the stored procedure
- Request body: JSON with crop yield data

#### List Records
- **GET** `/api/postgres/records/`
- Query parameters:
  - `limit` (default: 10, max: 100)
  - `offset` (default: 0)
  - `state` (optional, filter by state name)
  - `crop` (optional, filter by crop name)
  - `year` (optional, filter by crop year)

#### Get Latest Record
- **GET** `/api/postgres/records/latest`
- Returns the most recent crop yield record

#### Get Record by ID
- **GET** `/api/postgres/records/{record_id}`
- Returns a specific record by UUID

#### Update Record
- **PUT** `/api/postgres/records/{record_id}`
- Updates an existing record
- Request body: JSON with fields to update

#### Delete Record
- **DELETE** `/api/postgres/records/{record_id}`
- Deletes a record by UUID

### MongoDB Endpoints

Similar endpoints for MongoDB:
- **POST** `/api/mongodb/records/` - Create record
- **GET** `/api/mongodb/records/` - List records (with same query parameters)
- **GET** `/api/mongodb/records/latest` - Get latest record
- **GET** `/api/mongodb/records/{record_id}` - Get record by ID
- **PUT** `/api/mongodb/records/{record_id}` - Update record
- **DELETE** `/api/mongodb/records/{record_id}` - Delete record

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Example Requests

### Create PostgreSQL Record
```bash
curl -X POST "http://localhost:8000/api/postgres/records/" \
  -H "Content-Type: application/json" \
  -d '{
    "state_name": "Assam",
    "crop_name": "Rice",
    "season_name": "Autumn",
    "crop_year": 2021,
    "area": 607358,
    "production": 398311,
    "annual_rainfall": 2051.4,
    "fertilizer": 57802260.86,
    "pesticide": 188280.98,
    "yield": 0.780869565
  }'
```

### Create MongoDB Record
```bash
curl -X POST "http://localhost:8000/api/mongodb/records/" \
  -H "Content-Type: application/json" \
  -d '{
    "state_name": "Assam",
    "crop_name": "Rice",
    "season_name": "Autumn",
    "year": 2021,
    "area": 607358,
    "production": 398311,
    "annual_rainfall": 2051.4,
    "fertilizer": 57802260.86,
    "pesticide": 188280.98,
    "yield": 0.780869565
  }'
```

### List Records
```bash
curl "http://localhost:8000/api/postgres/records/?limit=10&offset=0&state=Assam&year=2021"
```

## Environment Variables

- `POSTGRES_HOST`: PostgreSQL host (default: localhost)
- `POSTGRES_DB`: Database name (default: agroyield)
- `POSTGRES_USER`: Database user (default: postgres)
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_PORT`: Database port (default: 5432)
- `MONGO_URI`: MongoDB connection string (default: mongodb://localhost:27017/)

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `204`: No Content (for DELETE)
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `409`: Conflict (duplicate records)
- `500`: Internal Server Error
