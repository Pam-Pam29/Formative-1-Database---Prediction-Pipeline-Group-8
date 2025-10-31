# Quick setup script for Render PostgreSQL database
# IMPORTANT: Set DATABASE_URL environment variable first!
# Example: $env:DATABASE_URL = "postgresql://user:password@host/database"

if (-not $env:DATABASE_URL) {
    Write-Host "[ERROR] DATABASE_URL not set!" -ForegroundColor Red
    Write-Host "Please set it first:" -ForegroundColor Yellow
    Write-Host '  $env:DATABASE_URL = "postgresql://user:password@host/database"' -ForegroundColor Cyan
    exit 1
}

$DATABASE_URL = $env:DATABASE_URL

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "RENDER DATABASE SETUP" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variable
$env:DATABASE_URL = $DATABASE_URL
Write-Host "DATABASE_URL set" -ForegroundColor Green
Write-Host ""

# Step 1: Create schema
Write-Host "Step 1: Creating schema..." -ForegroundColor Yellow
$connectionString = "$DATABASE_URL" + "?sslmode=require"
psql $connectionString -f "sql files\schema.sql"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Schema creation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Schema created" -ForegroundColor Green
Write-Host ""

# Step 2: Create stored procedure
Write-Host "Step 2: Creating stored procedure..." -ForegroundColor Yellow
psql $connectionString -f "sql files\procedures.sql"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Stored procedure creation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Stored procedure created" -ForegroundColor Green
Write-Host ""

# Step 3: Create triggers
Write-Host "Step 3: Creating triggers..." -ForegroundColor Yellow
psql $connectionString -f "sql files\triggers.sql"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Trigger creation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Triggers created" -ForegroundColor Green
Write-Host ""

# Step 4: Import data
Write-Host "Step 4: Importing data (this may take 5-10 minutes)..." -ForegroundColor Yellow
Write-Host "  This will import 19,690 records..." -ForegroundColor Gray
python import_data.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Data import failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Data imported" -ForegroundColor Green
Write-Host ""

# Step 5: Verify import
Write-Host "Step 5: Verifying import..." -ForegroundColor Yellow
psql $connectionString -c "SELECT COUNT(*) FROM states; SELECT COUNT(*) FROM crops; SELECT COUNT(*) FROM seasons; SELECT COUNT(*) FROM crop_yield_records;"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your database is now set up on Render!" -ForegroundColor Yellow
Write-Host "  Region: Frankfurt (EU Central)" -ForegroundColor Gray
Write-Host "  Database: agroyield" -ForegroundColor Gray
Write-Host ""
Write-Host "WARNING: Never commit credentials to GitHub!" -ForegroundColor Red
