# PowerShell script to set up PostgreSQL database on Render
# Run this script after creating your Render database

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "RENDER DATABASE SETUP" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Prompt for Render connection details
Write-Host "Enter your Render PostgreSQL connection details:" -ForegroundColor Yellow
$host = Read-Host "Database Host (e.g., dpg-xxxxx-a.oregon-postgres.render.com)"
$database = Read-Host "Database Name (e.g., agroyield)"
$user = Read-Host "Database User"
$password = Read-Host "Database Password" -AsSecureString
$port = Read-Host "Port (default: 5432)" 
if ([string]::IsNullOrWhiteSpace($port)) { $port = "5432" }

# Convert secure string to plain text
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
$plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Build connection string
$connectionString = "postgresql://${user}:${plainPassword}@${host}:${port}/${database}?sslmode=require"

Write-Host ""
Write-Host "Setting DATABASE_URL environment variable..." -ForegroundColor Green
$env:DATABASE_URL = $connectionString

Write-Host ""
Write-Host "Step 1: Creating schema..." -ForegroundColor Yellow
psql $connectionString -f "sql files\schema.sql"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Schema creation failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Creating stored procedure..." -ForegroundColor Yellow
psql $connectionString -f "sql files\procedures.sql"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Stored procedure creation failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Creating triggers..." -ForegroundColor Yellow
psql $connectionString -f "sql files\triggers.sql"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Trigger creation failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 4: Importing data (this may take 5-10 minutes)..." -ForegroundColor Yellow
python import_data.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Data import failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 5: Verifying import..." -ForegroundColor Yellow
psql $connectionString -c "SELECT 'States' as table_name, COUNT(*) as count FROM states UNION ALL SELECT 'Crops', COUNT(*) FROM crops UNION ALL SELECT 'Seasons', COUNT(*) FROM seasons UNION ALL SELECT 'Crop Yield Records', COUNT(*) FROM crop_yield_records;"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your DATABASE_URL is saved in this PowerShell session." -ForegroundColor Yellow
Write-Host "To use it later, set the environment variable:" -ForegroundColor Yellow
Write-Host '  $env:DATABASE_URL = "' + $connectionString + '"' -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  IMPORTANT: Never commit credentials to GitHub!" -ForegroundColor Red
Write-Host "   Use Render's Environment section or environment variables." -ForegroundColor Yellow

