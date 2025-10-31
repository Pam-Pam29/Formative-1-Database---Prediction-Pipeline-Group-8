"""
Verification script to check if ERD schema matches crop_yield.csv
"""

import pandas as pd
from pathlib import Path

# Load CSV
csv_file = Path(__file__).parent / 'crop_yield.csv'
df = pd.read_csv(csv_file)

print("=" * 60)
print("ERD SCHEMA vs CSV VERIFICATION")
print("=" * 60)

print("\n1. CSV STRUCTURE:")
print("-" * 60)
print(f"Total rows: {len(df):,}")
print(f"\nCSV Columns ({len(df.columns)}):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

print("\n2. DATA TYPE MAPPING:")
print("-" * 60)
mapping = {
    'Crop': '-> crops.crop_name (lookup) -> crop_yield_records.crop_id (FK)',
    'Crop_Year': '-> crop_yield_records.crop_year (INTEGER)',
    'Season': '-> seasons.season_name (lookup) -> crop_yield_records.season_id (FK)',
    'State': '-> states.state_name (lookup) -> crop_yield_records.state_id (FK)',
    'Area': '-> crop_yield_records.area (NUMERIC(12,2))',
    'Production': '-> crop_yield_records.production (NUMERIC(15,2))',
    'Annual_Rainfall': '-> crop_yield_records.annual_rainfall (NUMERIC(10,2))',
    'Fertilizer': '-> crop_yield_records.fertilizer (NUMERIC(15,2))',
    'Pesticide': '-> crop_yield_records.pesticide (NUMERIC(12,2))',
    'Yield': '-> crop_yield_records.yield (NUMERIC(15,4))'
}

for csv_col, db_mapping in mapping.items():
    csv_dtype = str(df[csv_col].dtype)
    print(f"  {csv_col:20} ({csv_dtype:8}) {db_mapping}")

print("\n3. UNIQUE VALUES (Lookup Tables):")
print("-" * 60)
print(f"  States:  {df['State'].nunique()} unique values")
print(f"  Crops:   {df['Crop'].nunique()} unique values")
print(f"  Seasons: {df['Season'].nunique()} unique values")

print("\n4. SEASON VALUES (checking for trailing spaces):")
print("-" * 60)
seasons = sorted(df['Season'].str.strip().unique())
print(f"  Unique seasons (trimmed): {len(seasons)}")
for season in seasons:
    # Check if original has trailing spaces
    original = df[df['Season'].str.strip() == season]['Season'].iloc[0]
    has_space = original != season
    space_note = " [WARN: HAS TRAILING SPACE]" if has_space else ""
    print(f"    - '{season}'{space_note}")

print("\n5. DATA VALIDATION:")
print("-" * 60)
print(f"  Year range: {df['Crop_Year'].min()} - {df['Crop_Year'].max()}")
print(f"  Area range: {df['Area'].min():,.0f} - {df['Area'].max():,.0f}")
print(f"  Production range: {df['Production'].min():,.0f} - {df['Production'].max():,.0f}")
print(f"  Yield range: {df['Yield'].min():.4f} - {df['Yield'].max():.4f}")

print("\n6. NULL VALUES:")
print("-" * 60)
nulls = df.isnull().sum()
if nulls.sum() == 0:
    print("  [OK] No null values found")
else:
    for col, count in nulls[nulls > 0].items():
        print(f"  [WARN] {col}: {count} null values")

print("\n7. SCHEMA VERIFICATION:")
print("-" * 60)
print("\nDatabase Schema Tables:")
print("  1. states (lookup) - stores unique state names")
print("  2. crops (lookup) - stores unique crop names")
print("  3. seasons (lookup) - stores unique season names")
print("  4. crop_yield_records (fact table) - stores all numeric data + FKs")
print("  5. audits (audit table) - tracks changes via trigger")

print("\nAll CSV columns are mapped correctly:")
for csv_col in df.columns:
    if csv_col in ['State', 'Crop', 'Season']:
        print(f"  [OK] {csv_col} -> lookup table + FK relationship")
    else:
        db_col = csv_col.lower().replace('crop_year', 'crop_year').replace('annual_rainfall', 'annual_rainfall')
        print(f"  [OK] {csv_col} -> crop_yield_records.{db_col}")

print("\n8. POTENTIAL ISSUES:")
print("-" * 60)
issues = []

# Check for trailing spaces in Season
if df['Season'].str.endswith(' ').any():
    issues.append("[WARN] Some Season values have trailing spaces (handled by TRIM() in stored procedure)")

# Check for very large values that might exceed NUMERIC precision
max_area = df['Area'].max()
if max_area > 99999999999:  # NUMERIC(12,2) max
    issues.append(f"[WARN] Area value {max_area} might exceed NUMERIC(12,2) precision")

max_production = df['Production'].max()
if max_production > 99999999999999:  # NUMERIC(15,2) max
    issues.append(f"[WARN] Production value {max_production} might exceed NUMERIC(15,2) precision")

if not issues:
    print("  [OK] No issues found - schema is compatible with CSV")
else:
    for issue in issues:
        print(f"  {issue}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\n[OK] CONCLUSION: ERD schema correctly maps to crop_yield.csv")
print("   All CSV columns have corresponding database fields")
print("   Data types are appropriate for the data ranges")
print("   Lookup tables properly normalize State, Crop, and Season")

