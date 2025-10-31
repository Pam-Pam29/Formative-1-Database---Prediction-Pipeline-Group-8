# Hosting PostgreSQL on Render

This guide will help you set up a PostgreSQL database on Render for your AgroYield project.

---

## Step 1: Create Render Account

1. Go to [https://render.com](https://render.com)
2. Sign up for a free account (GitHub OAuth is easiest)

---

## Step 2: Create PostgreSQL Database

1. **Navigate to Dashboard**
   - Click "New +" → "PostgreSQL"

2. **Configure Database**
   - **Name**: `agroyield` (or your preferred name)
   - **Database**: `agroyield`
   - **User**: `agroyield_user` (auto-generated, or choose your own)
   - **Region**: 
     - 🇪🇺 **For Africa**: Choose `Frankfurt (EU Central)` or `Ireland (EU West)` - closest to Africa with lowest latency
     - 🇺🇸 Alternative: `Oregon (US West)` or `Ohio (US East)` if EU regions are unavailable
     - 🇸🇬 Asia: `Singapore (AP Southeast)` - for East/Southern Africa
   - **PostgreSQL Version**: `14` or `15` (recommended)
   - **Plan**: **Free** (suitable for development/testing)
   
   💡 **Tip**: For Africa, **Frankfurt (EU Central)** typically offers the best connection speeds.

3. **Create Database**
   - Click "Create Database"
   - Wait 2-3 minutes for provisioning

---

## Step 3: Get Connection Details

Once your database is created:

1. **Copy Connection String**
   - Go to your database dashboard
   - Under "Connections" section
   - Copy the **"Internal Database URL"** (for apps on Render) or **"External Database URL"** (for local apps)

   Example format (Frankfurt region):
   ```
   postgresql://agroyield_user:password123@dpg-xxxxx-a.frankfurt-postgres.render.com/agroyield
   ```
   
   Note: The hostname will contain your selected region (e.g., `frankfurt`, `oregon`, `singapore`).

2. **Save Connection Details**
   - **Host**: `dpg-xxxxx-a.frankfurt-postgres.render.com` (or your selected region)
   - **Port**: `5432` (default)
   - **Database**: `agroyield`
   - **User**: `agroyield_user`
   - **Password**: (shown in dashboard, save securely!)

   ⚠️ **IMPORTANT**: Save these credentials - you won't see the password again!

---

## Step 4: Update Connection Scripts

### Option A: Update `import_data.py` for Render

Edit `db/postgres/import_data.py`:

```python
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from pathlib import Path
from getpass import getpass
from urllib.parse import urlparse

# Render Database Configuration
# Option 1: Use connection string (recommended)
RENDER_DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@host:5432/dbname')

# Option 2: Use individual components
DB_HOST = os.getenv('DB_HOST', 'dpg-xxxxx-a.oregon-postgres.render.com')
DB_NAME = os.getenv('DB_NAME', 'agroyield')
DB_USER = os.getenv('DB_USER', 'agroyield_user')
DB_PASSWORD = os.getenv('DB_PASSWORD')  # Set via environment variable or getpass
DB_PORT = os.getenv('DB_PORT', '5432')

def get_db_config():
    """Get database configuration from environment or user input"""
    # Try connection string first
    if 'DATABASE_URL' in os.environ:
        url = urlparse(os.environ['DATABASE_URL'])
        return {
            'host': url.hostname,
            'database': url.path[1:],  # Remove leading '/'
            'user': url.username,
            'password': url.password,
            'port': url.port or 5432
        }
    
    # Otherwise use individual components
    password = os.getenv('DB_PASSWORD')
    if not password:
        password = getpass(f'Enter PostgreSQL password for {DB_USER}: ')
    
    return {
        'host': DB_HOST,
        'database': DB_NAME,
        'user': DB_USER,
        'password': password,
        'port': int(DB_PORT)
    }

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        print("✓ Connected to PostgreSQL database on Render")
        return conn
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        raise

# Rest of the script remains the same...
```

### Option B: Create Environment File (`.env`)

Create `db/postgres/.env` (add to `.gitignore`):

```env
DATABASE_URL=postgresql://agroyield_user:your_password@dpg-xxxxx-a.oregon-postgres.render.com/agroyield

# Or separate variables:
DB_HOST=dpg-xxxxx-a.oregon-postgres.render.com
DB_NAME=agroyield
DB_USER=agroyield_user
DB_PASSWORD=your_password_here
DB_PORT=5432
```

---

## Step 5: Run SQL Scripts on Render

### Method 1: Using `psql` Command Line

```powershell
# Set environment variable with connection string
$env:DATABASE_URL = "postgresql://agroyield_user:password@dpg-xxxxx-a.oregon-postgres.render.com/agroyield"

# Run schema
psql $env:DATABASE_URL -f "db\postgres\sql files\schema.sql"

# Run stored procedure
psql $env:DATABASE_URL -f "db\postgres\sql files\procedures.sql"

# Run triggers
psql $env:DATABASE_URL -f "db\postgres\sql files\triggers.sql"
```

### Method 2: Using Python Script

```powershell
# Set environment variable
$env:DATABASE_URL = "postgresql://agroyield_user:password@dpg-xxxxx-a.oregon-postgres.render.com/agroyield"

# Or set individual variables
$env:DB_HOST = "dpg-xxxxx-a.oregon-postgres.render.com"
$env:DB_NAME = "agroyield"
$env:DB_USER = "agroyield_user"
$env:DB_PASSWORD = "your_password"

# Run import script
cd db\postgres
python import_data.py
```

---

## Step 6: Verify Connection

```powershell
# Test connection
psql $env:DATABASE_URL -c "SELECT 'States' as table_name, COUNT(*) as count FROM states UNION ALL SELECT 'Crops', COUNT(*) FROM crops UNION ALL SELECT 'Seasons', COUNT(*) FROM seasons UNION ALL SELECT 'Crop Yield Records', COUNT(*) FROM crop_yield_records;"
```

---

## Step 7: Important Notes for Render

### ⚠️ Security Best Practices

1. **Never commit credentials to GitHub**
   - Add `.env` to `.gitignore`
   - Use environment variables
   - Use Render's "Environment" section for secrets

2. **External vs Internal URLs**
   - **External URL**: Use when connecting from local machine
   - **Internal URL**: Use when connecting from other Render services (e.g., FastAPI app)

3. **Free Tier Limitations**
   - Database spins down after 90 days of inactivity (Free tier)
   - Connection limit: ~25 connections
   - Storage: 1 GB (sufficient for 19,690 records)

### Connection String Format

```
postgresql://[user]:[password]@[host]:[port]/[database]
```

Examples by region:

**For Africa (Recommended):**
```
# Frankfurt (EU Central) - Best for Africa
postgresql://agroyield_user:abc123@dpg-xxxxx-a.frankfurt-postgres.render.com:5432/agroyield

# Ireland (EU West) - Alternative
postgresql://agroyield_user:abc123@dpg-xxxxx-a.ireland-postgres.render.com:5432/agroyield
```

**Other regions:**
```
# Oregon (US West)
postgresql://agroyield_user:abc123@dpg-xxxxx-a.oregon-postgres.render.com:5432/agroyield

# Singapore (AP Southeast) - For East/Southern Africa
postgresql://agroyield_user:abc123@dpg-xxxxx-a.singapore-postgres.render.com:5432/agroyield
```

---

## Step 8: Update FastAPI for Task 2

When building your FastAPI app (Task 2), use:

```python
import os
from sqlalchemy import create_engine

# Get connection string from environment
DATABASE_URL = os.getenv('DATABASE_URL')

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
```

---

## Troubleshooting

### Connection Timeout
- **Issue**: Can't connect from local machine
- **Solution**: Use **External Database URL**, not Internal
- Check if your IP is whitelisted (Render Free tier allows all IPs)

### SSL Required
- **Issue**: `SSL connection required`
- **Solution**: Add `?sslmode=require` to connection string:
  ```
  postgresql://user:pass@host:5432/db?sslmode=require
  ```

### Database Not Found
- **Issue**: `database "agroyield" does not exist`
- **Solution**: 
  1. Check database name in Render dashboard
  2. Default database is `postgres`, create `agroyield` first:
     ```sql
     CREATE DATABASE agroyield;
     ```

### Import Takes Too Long
- **Issue**: Slow import on free tier
- **Solution**: 
  - Use Python script (better error handling)
  - Import in batches
  - Consider upgrading to Starter plan ($7/month) for better performance

---

## Quick Setup Checklist

- [ ] Create Render account
- [ ] Create PostgreSQL database
- [ ] Save connection credentials
- [ ] Update `import_data.py` with Render connection
- [ ] Run `schema.sql` on Render database
- [ ] Run `procedures.sql` on Render database
- [ ] Run `triggers.sql` on Render database
- [ ] Import data using `import_data.py`
- [ ] Verify data import (count records)
- [ ] Test stored procedure
- [ ] Test trigger/audit log

---

## Next Steps

1. **For Task 2 (FastAPI)**: Use the same database connection for your API endpoints
2. **For MongoDB**: Set up MongoDB Atlas (separate guide)
3. **Documentation**: Update README with hosted database details

---

**Support**: 
- Render Docs: https://render.com/docs/databases
- PostgreSQL on Render: https://render.com/docs/databases#postgresql

