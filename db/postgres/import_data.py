"""
Python script to import crop_yield.csv into PostgreSQL database
This is more efficient than SQL for large imports and provides better error handling
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from pathlib import Path
from getpass import getpass

# Database connection parameters
DB_HOST = 'localhost'
DB_NAME = 'agroyield'
DB_USER = 'postgres'
DB_PORT = 5432

def get_db_config():
    """Get database configuration, prompting for password if needed"""
    password = os.getenv('PGPASSWORD')
    if not password:
        password = getpass(f'Enter PostgreSQL password for user {DB_USER}: ')
    return {
        'host': DB_HOST,
        'database': DB_NAME,
        'user': DB_USER,
        'password': password,
        'port': DB_PORT
    }

# CSV file path
CSV_FILE = Path(__file__).parent.parent.parent / 'crop_yield.csv'

def connect_db():
    """Establish database connection"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        print("✓ Connected to PostgreSQL database")
        return conn
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        raise

def import_lookup_tables(conn, df):
    """Import unique values into states, crops, and seasons tables"""
    cursor = conn.cursor()
    
    try:
        # Import states
        states = df['State'].str.strip().dropna().unique()
        for state in states:
            cursor.execute(
                "INSERT INTO states (state_name) VALUES (%s) ON CONFLICT (state_name) DO NOTHING",
                (state,)
            )
        print(f"✓ Imported {len(states)} unique states")
        
        # Import crops
        crops = df['Crop'].str.strip().dropna().unique()
        for crop in crops:
            cursor.execute(
                "INSERT INTO crops (crop_name) VALUES (%s) ON CONFLICT (crop_name) DO NOTHING",
                (crop,)
            )
        print(f"✓ Imported {len(crops)} unique crops")
        
        # Import seasons
        seasons = df['Season'].str.strip().dropna().unique()
        for season in seasons:
            cursor.execute(
                "INSERT INTO seasons (season_name) VALUES (%s) ON CONFLICT (season_name) DO NOTHING",
                (season,)
            )
        print(f"✓ Imported {len(seasons)} unique seasons")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error importing lookup tables: {e}")
        raise
    finally:
        cursor.close()

def import_yield_records(conn, df):
    """Import crop yield records using the stored procedure"""
    cursor = conn.cursor()
    
    total_records = len(df)
    success_count = 0
    error_count = 0
    
    print(f"\nImporting {total_records} records...")
    
    for idx, row in df.iterrows():
        try:
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
            
            # Progress indicator
            if (idx + 1) % 1000 == 0:
                print(f"  Progress: {idx + 1}/{total_records} ({success_count} successful, {error_count} errors)")
                conn.commit()  # Commit in batches for better performance
            
        except Exception as e:
            error_count += 1
            if error_count <= 10:  # Print first 10 errors
                print(f"  ✗ Error on row {idx + 1}: {e}")
    
    conn.commit()
    print(f"\n✓ Import complete!")
    print(f"  Successful: {success_count}")
    print(f"  Errors: {error_count}")
    
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
        print(f"✗ Error verifying import: {e}")
    finally:
        cursor.close()

def main():
    """Main import function"""
    print("="*50)
    print("CROP YIELD DATA IMPORT")
    print("="*50)
    
    # Load CSV
    print(f"\nLoading CSV from: {CSV_FILE}")
    if not CSV_FILE.exists():
        print(f"✗ Error: CSV file not found at {CSV_FILE}")
        return
    
    df = pd.read_csv(CSV_FILE)
    print(f"✓ Loaded {len(df):,} records from CSV")
    
    # Connect to database
    conn = connect_db()
    
    try:
        # Import lookup tables
        print("\nStep 1: Importing lookup tables...")
        import_lookup_tables(conn, df)
        
        # Import yield records
        print("\nStep 2: Importing crop yield records...")
        import_yield_records(conn, df)
        
        # Verify import
        verify_import(conn)
        
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        raise
    finally:
        conn.close()
        print("\n✓ Database connection closed")

if __name__ == '__main__':
    main()

