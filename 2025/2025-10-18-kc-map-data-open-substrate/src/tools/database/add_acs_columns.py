#!/usr/bin/env python3
"""
Add ACS columns to block_groups table

This script adds the necessary columns to the block_groups table
for storing ACS demographic data.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from web.config import config
import pandas as pd

def add_acs_columns():
    """Add ACS demographic columns to tiger_boundaries.gpkg"""
    
    try:
        import geopandas as gpd
        
        # Path to TIGER GeoPackage
        tiger_path = Path(__file__).parent.parent.parent / "data" / "processed" / "tiger_boundaries.gpkg"
        
        if not tiger_path.exists():
            print("ERROR: tiger_boundaries.gpkg not found.")
            print("Please run the TIGER boundaries ETL first:")
            print("  python tools/etl/load_tiger_boundaries.py")
            return
        
        print(f"Reading {tiger_path}...")
        gdf = gpd.read_file(tiger_path, layer='bg')
        
        # Define all ACS columns with their data types
        # This matches the variables defined in load_acs_data.py
        acs_columns = {
            # Core demographics
            'population': 'int64',
            'median_household_income': 'int64',
            'mhi_moe': 'int64',
            'poverty_universe': 'int64',
            'poverty_count': 'int64',
            'poverty_rate': 'float64',
            'total_race': 'int64',
            'white_alone': 'int64',
            'black_alone': 'int64',
            'hispanic_latino': 'int64',
            'median_age': 'float64',
            
            # Health insurance
            'health_insurance_universe': 'int64',
            'with_health_insurance': 'int64',
            'with_private_insurance': 'int64',
            'with_public_insurance': 'int64',
            'without_health_insurance': 'int64',
            
            # Disability
            'disability_universe': 'int64',
            'with_disability': 'int64',
            'without_disability': 'int64',
            
            # Veteran status
            'veteran_universe': 'int64',
            'veteran_status_with_flag': 'int64',
            'veteran_status_without_flag': 'int64',
            
            # Language
            'language_universe': 'int64',
            'english_only': 'int64',
            'spanish_speak_limited_english': 'int64',
            'other_language_speak_limited_english': 'int64',
            
            # Income brackets
            'income_universe': 'int64',
            'income_less_10000': 'int64',
            'income_10000_14999': 'int64',
            'income_15000_19999': 'int64',
            'income_20000_24999': 'int64',
            'income_25000_29999': 'int64',
            'income_30000_34999': 'int64',
            'income_35000_39999': 'int64',
            'income_40000_44999': 'int64',
            'income_45000_49999': 'int64',
            'income_50000_59999': 'int64',
            'income_60000_74999': 'int64',
            'income_75000_99999': 'int64',
            'income_100000_124999': 'int64',
            'income_125000_149999': 'int64',
            'income_150000_199999': 'int64',
            'income_200000_or_more': 'int64',
            
            # Housing year built
            'year_built_universe': 'int64',
            'built_2014_later': 'int64',
            'built_2010_2013': 'int64',
            'built_2000_2009': 'int64',
            'built_1990_1999': 'int64',
            'built_1980_1989': 'int64',
            'built_1970_1979': 'int64',
            'built_1960_1969': 'int64',
            'built_1950_1959': 'int64',
            'built_1940_1949': 'int64',
            'built_1939_or_earlier': 'int64',
            
            # Housing units
            'housing_units_universe': 'int64',
            'single_unit_detached': 'int64',
            'single_unit_attached': 'int64',
            'units_2_4': 'int64',
            'units_5_9': 'int64',
            'units_10_19': 'int64',
            'units_20_49': 'int64',
            'units_50_or_more': 'int64',
            'mobile_home': 'int64',
            'boat_rv_van_etc': 'int64',
            
            # Vehicle availability
            'vehicle_universe': 'int64',
            'no_vehicles': 'int64',
            'one_vehicle': 'int64',
            'two_vehicles': 'int64',
            'three_vehicles': 'int64',
            'four_or_more_vehicles': 'int64',
            
            # Housing cost burden
            'cost_burden_universe': 'int64',
            'housing_cost_less_20pct': 'int64',
            'housing_cost_20_24pct': 'int64',
            'housing_cost_25_29pct': 'int64',
            'housing_cost_30_34pct': 'int64',
            'housing_cost_35pct_or_more': 'int64',
            
            # Citizenship
            'nativity_universe': 'int64',
            'native_born': 'int64',
            'naturalized_citizen': 'int64',
            'not_us_citizen': 'int64',
            
            # Family structure
            'family_universe': 'int64',
            'family_households': 'int64',
            'married_couple_families': 'int64',
            'single_male_families': 'int64',
            'single_female_families': 'int64',
            'non_family_households': 'int64',
            
            # Detailed race categories
            'american_indian_alone': 'int64',
            'asian_alone': 'int64',
            'native_hawaiian_pi_alone': 'int64',
            'some_other_race_alone': 'int64',
            'two_or_more_races': 'int64',
            'two_races_including_other': 'int64',
            'two_races_excluding_other': 'int64',
            
            # Hispanic origin detailed
            'not_hispanic_latino': 'int64',
            'hispanic_mexican': 'int64',
            'hispanic_puerto_rican': 'int64',
            'hispanic_cuban': 'int64',
            'hispanic_central_american': 'int64',
            'hispanic_south_american': 'int64',
            'hispanic_other': 'int64',
            
            # Housing physical characteristics - Bedrooms
            'owner_bedrooms_0': 'int64',
            'owner_bedrooms_1': 'int64',
            'owner_bedrooms_2': 'int64',
            'owner_bedrooms_3plus': 'int64',
            'renter_bedrooms_0': 'int64',
            'renter_bedrooms_1': 'int64',
            'renter_bedrooms_2': 'int64',
            'renter_bedrooms_3plus': 'int64',
            
            # Housing - Year moved in
            'moved_in_2015_2016': 'int64',
            'moved_in_2010_2014': 'int64',
            'moved_in_2000_2009': 'int64',
            'moved_in_1990_1999': 'int64',
            'moved_in_1980_1989': 'int64',
            'moved_in_1979_earlier': 'int64',
            
            # Computer and internet access
            'computer_with_broadband': 'int64',
            'computer_without_broadband': 'int64',
            'smartphone_only': 'int64',
            'no_computer': 'int64',
            'internet_subscription_dialup': 'int64',
            'internet_subscription_dsl': 'int64',
            'internet_subscription_cable': 'int64',
            'internet_subscription_fiber': 'int64',
            'internet_subscription_cellular': 'int64',
            'internet_subscription_satellite': 'int64',
            
            # Detailed occupation (top categories)
            'occ_management': 'int64',
            'occ_business_financial': 'int64',
            'occ_computer_math': 'int64',
            'occ_architecture_engineering': 'int64',
            'occ_life_physical_science': 'int64',
            'occ_social_service': 'int64',
            'occ_legal': 'int64',
            'occ_education': 'int64',
            'occ_healthcare_practitioners': 'int64',
            'occ_protective_service': 'int64',
            'occ_food_prep_service': 'int64',
            'occ_building_grounds': 'int64',
            'occ_personal_care': 'int64',
            'occ_sales': 'int64',
            'occ_office_admin': 'int64',
            'occ_construction': 'int64',
            'occ_extraction': 'int64',
            'occ_installation_maintenance': 'int64',
            'occ_production': 'int64',
            'occ_transportation': 'int64',
            
            # Detailed industry (top categories)
            'ind_agriculture': 'int64',
            'ind_mining': 'int64',
            'ind_utilities': 'int64',
            'ind_construction': 'int64',
            'ind_manufacturing': 'int64',
            'ind_wholesale_trade': 'int64',
            'ind_retail_trade': 'int64',
            'ind_transportation': 'int64',
            'ind_information': 'int64',
            'ind_finance_insurance': 'int64',
            'ind_real_estate': 'int64',
            'ind_professional_scientific': 'int64',
            'ind_management': 'int64',
            'ind_educational': 'int64',
            'ind_healthcare': 'int64',
            'ind_arts_entertainment': 'int64',
            'ind_accommodation_food': 'int64',
            'ind_other_services': 'int64',
            'ind_public_admin': 'int64',
            
            # Commute time
            'commute_5_9_min': 'int64',
            'commute_10_14_min': 'int64',
            'commute_15_19_min': 'int64',
            'commute_20_24_min': 'int64',
            'commute_25_29_min': 'int64',
            'commute_30_34_min': 'int64',
            'commute_35_39_min': 'int64',
            'commute_40_44_min': 'int64',
            'commute_45_59_min': 'int64',
            'commute_60_89_min': 'int64',
            'commute_90plus_min': 'int64',
            
            # Migration/mobility
            'same_house_1yr': 'int64',
            'moved_same_county': 'int64',
            'moved_diff_county_same_state': 'int64',
            'moved_diff_state': 'int64',
            'moved_from_abroad': 'int64',
            
            # Marital status
            'never_married': 'int64',
            'now_married': 'int64',
            'separated': 'int64',
            'divorced': 'int64',
            'widowed': 'int64',
            
            # Fertility
            'women_15_50': 'int64',
            'women_with_birth_past_year': 'int64',
            'women_no_birth_past_year': 'int64',
            
            # Grandparents
            'grandparents_living_with_grandchildren': 'int64',
            'grandparents_responsible': 'int64',
            
            # Group quarters
            'group_quarters_total': 'int64',
            'institutionalized': 'int64',
            'non_institutionalized': 'int64',
            
            # School enrollment
            'enrolled_nursery': 'int64',
            'enrolled_elementary': 'int64',
            'enrolled_middle_high': 'int64',
            'enrolled_college': 'int64',
            'not_enrolled': 'int64',
            
            # Income by source
            'income_wages_salary': 'int64',
            'income_self_employment': 'int64',
            'income_interest': 'int64',
            'income_dividends': 'int64',
            'income_rental': 'int64',
            'income_social_security': 'int64',
            'income_retirement': 'int64',
            'income_ssi': 'int64',
            'income_public_assistance': 'int64',
            'income_snap': 'int64',
            
            # Metadata
            'acs_year': 'object',
            'acs_release': 'object'
        }
        
        added_count = 0
        for col_name, dtype in acs_columns.items():
            if col_name not in gdf.columns:
                # Initialize as None/NaN values instead of type
                if dtype == 'int64':
                    gdf[col_name] = None
                    gdf[col_name] = gdf[col_name].astype('Int64')  # Nullable integer
                elif dtype == 'float64':
                    gdf[col_name] = None
                    gdf[col_name] = gdf[col_name].astype('float64')
                else:
                    gdf[col_name] = None
                print(f"Adding column: {col_name} ({dtype})")
                added_count += 1
        
        if added_count > 0:
            print(f"\nSaving updated GeoPackage...")
            gdf.to_file(tiger_path, layer='bg', driver='GPKG')
            print(f"Added {added_count} ACS columns")
        else:
            print("ACS columns already exist")
            
        print("\nACS columns ready in tiger_boundaries.gpkg!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_acs_columns()

