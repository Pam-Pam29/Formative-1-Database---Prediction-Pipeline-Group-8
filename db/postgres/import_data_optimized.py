"""
Optimized import script that skips already imported records
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from pathlib import Path
from getpass import getpass
from urllib.parse import urlparse
import time

# Database connection parameters
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'agroyield')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PORT = int(os.getenv('DB_PORT', '5432'))

def get_db_config():
    """Get database configuration from environment variables or user input."""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        url = urlparse(database_url)
        return {
            'host': url.hostname,
            'database': url.path[1:] if url.path else DB_NAME,
            'user': url.username,
            'password': url.password,
            'port': url.port or DB_PORT,
            'sslmode': 'require' if 'render.com' in url.hostname else 'prefer'
        }
    
    password = os.getenv('DB_PASSWORD') or os.getenv('PGPASSWORD')
    if not password:
        password = getpass(f'Enter PostgreSQL password for user {DB_USER}: ')
    
    return {
        'host': DB_HOST,
        'database': DB_NAME,
        'user': DB_USER,
        'password': password,
        'port': DB_PORT
    }

CSV_FILE = Path(__file__).parent / 'crop_yield.csv'

def connect_db():
    """Establish database connection"""
    try:
        db_config = get_db_config()
        is_render = 'render.com' in db_config.get('host', '')
        sslmode = db_config.pop('sslmode', None)
        
        if is_render or sslmode:
            conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            if sslmode:
                conn_str += f"?sslmode={sslmode}"
            conn = psycopg2.connect(conn_str)
            print("[OK] Connected to PostgreSQL database on Render")
        else:
            conn = psycopg2.connect(**db_config)
            print("[OK] Connected to PostgreSQL database (local)")
        
        return conn
    except Exception as e:
        print(f"[ERROR] Error connecting to database: {e}")
        raise

def get_existing_records(conn):
    """Get set of already imported records to skip"""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT s.state_name, c.crop_name, se.season_name, r.crop_year
            FROM crop_yield_records r
            JOIN states s ON r.state_id = s.state_id
            JOIN crops c ON r.crop_id = c.crop_id
            JOIN seasons se ON r.season_id = se.season_id
        """)
        existing = set(cursor.fetchall())
        print(f"[INFO] Found {len(existing):,} existing records - will skip duplicates")
        return existing
    finally:
        cursor.close()

def import_remaining_records(conn, df, existing):
    """Import only records that don't exist yet"""
    cursor = conn.cursor()
    
    total_records = len(df)
    success_count = 0
    skip_count = 0
    error_count = 0
    start_time = time.time()
    
    print(f"\nImporting {total_records:,} records...")
    print(f"Progress will update every 100 records\n")
    
    for idx, row in df.iterrows():
        try:
            # Check if record already exists
            record_key = (
                str(row['State']).strip(),
                str(row['Crop']).strip(),
                str(row['Season']).strip(),
                int(row['Crop_Year'])
            )
            
            if record_key in existing:
                skip_count += 1
                continue
            
            # Call stored procedure
            cursor.callproc('sp_insert_crop_yield_record', [
                str(row['State']).strip() if pd.notna(row['State']) else None,
                str(row['Crop']).strip() if pd.notna(row['Crop']) else None,
                str(row['Season']).strip() if pd.notna(row['Season']) else None,
                int(row['Crop_Year']) if pd.notna(row['Crop_Year']) else None,
                float(row['Area']) if pd.notna(row['Area']) else None,
                float(row['Production']) if pd.notna(row['Production']) else None,
                float(row['Annual_Rainfall']) if pd.notna(row['Annual_Rainfall']) else None,
                float(row['Fertilizer']) if pd.notna(row['Fertilizer']) else None,
                float(row['Pesticide']) if pd.notna(row['Pesticide']) else None,
                float(row['Yield']) if pd.notna(row['Yield']) else None,
            ])
            
            success_count += 1
            existing.add(record_key)  # Track as imported
            
            # Progress indicator - every 100 records
            if (success_count + skip_count + error_count) % 100 == 0:
                elapsed = time.time() - start_time
                rate = success_count / elapsed if elapsed > 0 else 0
                remaining = total_records - (success_count + skip_count + error_count)
                eta_seconds = remaining / rate if rate > 0 else 0
                eta_minutes = eta_seconds / 60
                
                print(f"  Progress: {success_count + skip_count + error_count:,}/{total_records:,} | "
                      f"Imported: {success_count:,} | Skipped: {skip_count:,} | "
                      f"Errors: {error_count:,} | Rate: {rate:.1f} rec/s | "
                      f"ETA: {eta_minutes:.1f} min", flush=True)
                conn.commit()  # Commit in batches
            
        except Exception as e:
            error_count += 1
            if error_count <= 5:  # Print first 5 errors only
                print(f"  [ERROR] Row {idx + 1}: {str(e)[:100]}")
    
    conn.commit()
    elapsed_total = time.time() - start_time
    
    print(f"\n[OK] Import complete!")
    print(f"  Successful: {success_count:,}")
    print(f"  Skipped (already exist): {skip_count:,}")
    print(f"  Errors: {error_count:,}")
    print(f"  Total time: {elapsed_total/60:.1f} minutes")
    print(f"  Average rate: {success_count/elapsed_total:.1f} records/second" if elapsed_total > 0 else "")
    
    cursor.close()

def verify_import(conn):
    """Verify the import by checking record counts"""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 'States' as table_name, COUNT(*) as count FROM states
            UNION ALL
            SELECT 'Crops', COUNT(*) FROM crops
            UNION ALL
            SELECT 'Seasons', COUNT(*) FROM seasons
            UNION ALL
            SELECT 'Crop Yield Records', COUNT(*) FROM crop_yield_records
        """)
        
        results = cursor.fetchall()
        print("\n" + "="*50)
        print("IMPORT VERIFICATION")
        print("="*50)
        for table_name, count in results:
            print(f"  {table_name:25} : {count:,}")
    except Exception as e:
        print(f"[ERROR] Error verifying import: {e}")
    finally:
        cursor.close()

def main():
    """Main import function"""
    print("="*50)
    print("OPTIMIZED CROP YIELD DATA IMPORT")
    print("="*50)
    
    # Load CSV
    print(f"\nLoading CSV from: {CSV_FILE}")
    if not CSV_FILE.exists():
        print(f"[ERROR] Error: CSV file not found at {CSV_FILE}")
        return
    
    df = pd.read_csv(CSV_FILE)
    print(f"[OK] Loaded {len(df):,} records from CSV")
    
    # Connect to database
    conn = connect_db()
    
    try:
        # Get existing records
        print("\nChecking for existing records...")
        existing = get_existing_records(conn)
        
        # Import remaining records
        print("\nStarting import of new records...")
        import_remaining_records(conn, df, existing)
        
        # Verify import
        verify_import(conn)
        
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        raise
    finally:
        conn.close()
        print("\n[OK] Database connection closed")

if __name__ == '__main__':
    main()

