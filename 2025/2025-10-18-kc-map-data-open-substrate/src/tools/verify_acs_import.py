#!/usr/bin/env python3
"""
Verify ACS Data Import

This script checks what ACS data has been imported and displays sample data.
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path

project_root = Path(__file__).parent.parent
db_path = project_root / "data" / "processed" / "tiger_boundaries.gpkg"

print("Loading block groups from database...")
gdf = gpd.read_file(db_path, layer='bg')

print(f"\n{'='*60}")
print(f"ACS DATA IMPORT VERIFICATION")
print(f"{'='*60}")
print(f"\nTotal Block Groups: {len(gdf)}")
print(f"Total Columns: {len(gdf.columns)}")

# Count non-null values for key categories
print(f"\n{'='*60}")
print("IMPORT STATUS BY CATEGORY")
print(f"{'='*60}")

categories = {
    'Core Demographics': ['population', 'median_household_income', 'median_age', 'poverty_rate'],
    'Computer/Internet': ['computer_with_broadband', 'smartphone_only', 'no_computer'],
    'Detailed Race': ['american_indian_alone', 'asian_alone', 'two_or_more_races'],
    'Migration': ['same_house_1yr', 'moved_diff_state', 'moved_from_abroad'],
    'Marital Status': ['never_married_male', 'now_married_male', 'never_married_female'],
    'Grandparents': ['grandparents_living_with_grandchildren', 'grandparents_responsible'],
    'School Enrollment': ['enrolled_nursery', 'enrolled_elementary', 'enrolled_college'],
    'Commute Time': ['commute_5_9_min', 'commute_30_34_min', 'commute_90plus_min'],
}

for category, cols in categories.items():
    found_cols = []
    null_counts = {}
    
    for col in cols:
        if col in gdf.columns:
            found_cols.append(col)
            null_count = gdf[col].isna().sum()
            not_null_count = (gdf[col].notna()).sum()
            null_counts[col] = (not_null_count, null_count)
    
    if found_cols:
        print(f"\n[OK] {category}")
        for col, (not_null, null) in null_counts.items():
            pct = (not_null / len(gdf)) * 100
            print(f"   {col}: {not_null}/{len(gdf)} block groups ({pct:.1f}%) have data")
    else:
        print(f"\n[X] {category}: Not imported")

# Show sample data
print(f"\n{'='*60}")
print("SAMPLE DATA (First Block Group)")
print(f"{'='*60}")

sample = gdf.iloc[0]
print(f"\nGEOID: {sample['GEOID']}")
if 'countyfp' in gdf.columns:
    print(f"County: {sample['countyfp']}")
elif 'county' in gdf.columns:
    print(f"County: {sample['county']}")

if pd.notna(sample['population']):
    print(f"Population: {int(sample['population']):,}")
else:
    print("Population: No data")

if pd.notna(sample['median_household_income']):
    print(f"Median Household Income: ${int(sample['median_household_income']):,}")
else:
    print("Median Household Income: No data")

# Check new data
print(f"\nNew Categories:")
if 'computer_with_broadband' in gdf.columns and pd.notna(sample['computer_with_broadband']):
    print(f"  Computer with Broadband: {int(sample['computer_with_broadband'])}")

if 'asian_alone' in gdf.columns and pd.notna(sample['asian_alone']):
    print(f"  Asian Population: {int(sample['asian_alone'])}")

if 'same_house_1yr' in gdf.columns and pd.notna(sample['same_house_1yr']):
    print(f"  Same House 1 Year: {int(sample['same_house_1yr'])}")

if 'grandparents_responsible' in gdf.columns and pd.notna(sample['grandparents_responsible']):
    print(f"  Grandparents Responsible: {int(sample['grandparents_responsible'])}")

if 'enrolled_college' in gdf.columns and pd.notna(sample['enrolled_college']):
    print(f"  Enrolled in College: {int(sample['enrolled_college'])}")

if 'commute_30_34_min' in gdf.columns and pd.notna(sample['commute_30_34_min']):
    print(f"  Commute 30-34 Minutes: {int(sample['commute_30_34_min'])}")

print(f"\n{'='*60}")
print("VERIFICATION COMPLETE")
print(f"{'='*60}")

