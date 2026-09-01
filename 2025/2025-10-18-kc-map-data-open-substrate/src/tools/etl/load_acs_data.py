#!/usr/bin/env python3
"""
ACS (American Community Survey) Data ETL Script

Fetches ACS 5-year demographic data from the Census API and loads it
into the block_groups table in the main database.

Data Source: https://api.census.gov/data/2023/acs/acs5
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import pandas as pd
    import requests
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required packages. Install with: pip install pandas requests python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv(project_root / '.env')

# ACS Configuration
ACS_BASE_URL = 'https://api.census.gov/data/2023/acs/acs5'
ACS_YEAR = '2019-2023'
ACS_RELEASE = '2023-12-12'  # Release date of 2019-2023 data

# ACS Variables by Category for Batch Importing

# Core variables (always imported)
ACS_CORE_VARIABLES = {
    'B01001_001E': 'total_population',
    'B19013_001E': 'median_household_income',
    'B19013_001M': 'mhi_moe',
    'B03002_001E': 'total_race',
    'B03002_003E': 'white_alone',
    'B03002_004E': 'black_alone',
    'B03002_012E': 'hispanic_latino',
    'B01002_001E': 'median_age',
    'B17001_001E': 'poverty_universe',
    'B17001_002E': 'poverty_count',
}

# Age distribution (detailed brackets)
ACS_AGE_VARIABLES = {
    # Males under 18
    'B01001_003E': 'male_under_5',
    'B01001_004E': 'male_5_9',
    'B01001_005E': 'male_10_14',
    'B01001_006E': 'male_15_17',
    # Females under 18
    'B01001_027E': 'female_under_5',
    'B01001_028E': 'female_5_9',
    'B01001_029E': 'female_10_14',
    'B01001_030E': 'female_15_17',
    # Males 18-64
    'B01001_007E': 'male_18_19',
    'B01001_008E': 'male_20',
    'B01001_009E': 'male_21',
    'B01001_010E': 'male_22_24',
    'B01001_011E': 'male_25_29',
    'B01001_012E': 'male_30_34',
    'B01001_013E': 'male_35_39',
    'B01001_014E': 'male_40_44',
    'B01001_015E': 'male_45_49',
    'B01001_016E': 'male_50_54',
    'B01001_017E': 'male_55_59',
    'B01001_018E': 'male_60_61',
    'B01001_019E': 'male_62_64',
    # Females 18-64
    'B01001_031E': 'female_18_19',
    'B01001_032E': 'female_20',
    'B01001_033E': 'female_21',
    'B01001_034E': 'female_22_24',
    'B01001_035E': 'female_25_29',
    'B01001_036E': 'female_30_34',
    'B01001_037E': 'female_35_39',
    'B01001_038E': 'female_40_44',
    'B01001_039E': 'female_45_49',
    'B01001_040E': 'female_50_54',
    'B01001_041E': 'female_55_59',
    'B01001_042E': 'female_60_61',
    'B01001_043E': 'female_62_64',
    # Males 65+
    'B01001_020E': 'male_65_66',
    'B01001_021E': 'male_67_69',
    'B01001_022E': 'male_70_74',
    'B01001_023E': 'male_75_79',
    'B01001_024E': 'male_80_84',
    'B01001_025E': 'male_85_over',
    # Females 65+
    'B01001_044E': 'female_65_66',
    'B01001_045E': 'female_67_69',
    'B01001_046E': 'female_70_74',
    'B01001_047E': 'female_75_79',
    'B01001_048E': 'female_80_84',
    'B01001_049E': 'female_85_over',
}

# Housing characteristics
ACS_HOUSING_VARIABLES = {
    'B25002_002E': 'housing_occupied',
    'B25002_003E': 'housing_vacant',
    'B25003_002E': 'owner_occupied',
    'B25003_003E': 'renter_occupied',
    'B25077_001E': 'median_home_value',
    'B25064_001E': 'median_rent',
    'B25001_001E': 'total_housing_units',
}

# Education attainment
ACS_EDUCATION_VARIABLES = {
    'B15003_001E': 'education_universe',
    'B15003_017E': 'high_school_grad',
    'B15003_022E': 'bachelors_degree',
    'B15003_023E': 'masters_degree',
    'B15003_024E': 'professional_degree',
    'B15003_025E': 'doctorate_degree',
}

# Employment status
ACS_EMPLOYMENT_VARIABLES = {
    'B23025_001E': 'employment_universe',
    'B23025_002E': 'in_labor_force',
    'B23025_004E': 'employed',
    'B23025_005E': 'unemployed',
}

# Commuting patterns
ACS_COMMUTE_VARIABLES = {
    'B08301_001E': 'commute_universe',
    'B08301_003E': 'drove_alone',
    'B08301_010E': 'public_transit',
    'B08301_019E': 'walked',
    'B08301_021E': 'work_from_home',
    'B08301_020E': 'bicycle',
    'B08301_002E': 'carpooled',
}

# Health insurance coverage
ACS_HEALTH_INSURANCE_VARIABLES = {
    'B27001_001E': 'health_insurance_universe',
    'B27001_004E': 'with_health_insurance',
    'B27001_005E': 'with_private_insurance',
    'B27001_006E': 'with_public_insurance',
    'B27001_007E': 'without_health_insurance',
}

# Disability status
ACS_DISABILITY_VARIABLES = {
    'B18101_001E': 'disability_universe',
    'B18101_002E': 'with_disability',
    'B18101_003E': 'without_disability',
}

# Veteran status
ACS_VETERAN_VARIABLES = {
    'B21001_001E': 'veteran_universe',
    'B21001_002E': 'veteran_status_with_flag',
    'B21001_003E': 'veteran_status_without_flag',
}

# Language spoken at home
ACS_LANGUAGE_VARIABLES = {
    'B16007_001E': 'language_universe',
    'B16007_003E': 'english_only',
    'B16007_009E': 'spanish_speak_limited_english',
    'B16007_013E': 'other_language_speak_limited_english',
}

# Income distribution
ACS_INCOME_BRACKETS_VARIABLES = {
    'B19001_001E': 'income_universe',
    'B19001_002E': 'income_less_10000',
    'B19001_003E': 'income_10000_14999',
    'B19001_004E': 'income_15000_19999',
    'B19001_005E': 'income_20000_24999',
    'B19001_006E': 'income_25000_29999',
    'B19001_007E': 'income_30000_34999',
    'B19001_008E': 'income_35000_39999',
    'B19001_009E': 'income_40000_44999',
    'B19001_010E': 'income_45000_49999',
    'B19001_011E': 'income_50000_59999',
    'B19001_012E': 'income_60000_74999',
    'B19001_013E': 'income_75000_99999',
    'B19001_014E': 'income_100000_124999',
    'B19001_015E': 'income_125000_149999',
    'B19001_016E': 'income_150000_199999',
    'B19001_017E': 'income_200000_or_more',
}

# Housing year built
ACS_HOUSING_YEAR_BUILT_VARIABLES = {
    'B25034_001E': 'year_built_universe',
    'B25034_002E': 'built_2014_later',
    'B25034_003E': 'built_2010_2013',
    'B25034_004E': 'built_2000_2009',
    'B25034_005E': 'built_1990_1999',
    'B25034_006E': 'built_1980_1989',
    'B25034_007E': 'built_1970_1979',
    'B25034_008E': 'built_1960_1969',
    'B25034_009E': 'built_1950_1959',
    'B25034_010E': 'built_1940_1949',
    'B25034_011E': 'built_1939_or_earlier',
}

# Housing units in structure
ACS_HOUSING_UNITS_VARIABLES = {
    'B25024_001E': 'housing_units_universe',
    'B25024_002E': 'single_unit_detached',
    'B25024_003E': 'single_unit_attached',
    'B25024_004E': 'units_2_4',
    'B25024_005E': 'units_5_9',
    'B25024_006E': 'units_10_19',
    'B25024_007E': 'units_20_49',
    'B25024_008E': 'units_50_or_more',
    'B25024_009E': 'mobile_home',
    'B25024_010E': 'boat_rv_van_etc',
}

# Vehicle availability
ACS_VEHICLE_AVAILABILITY_VARIABLES = {
    'B25044_001E': 'vehicle_universe',
    'B25044_003E': 'no_vehicles',
    'B25044_004E': 'one_vehicle',
    'B25044_005E': 'two_vehicles',
    'B25044_006E': 'three_vehicles',
    'B25044_007E': 'four_or_more_vehicles',
}

# Housing cost burden
ACS_HOUSING_COST_BURDEN_VARIABLES = {
    'B25106_001E': 'cost_burden_universe',
    'B25106_012E': 'housing_cost_less_20pct',
    'B25106_013E': 'housing_cost_20_24pct',
    'B25106_014E': 'housing_cost_25_29pct',
    'B25106_015E': 'housing_cost_30_34pct',
    'B25106_016E': 'housing_cost_35pct_or_more',
}

# Citizenship and nativity
ACS_CITIZENSHIP_VARIABLES = {
    'B05001_001E': 'nativity_universe',
    'B05001_002E': 'native_born',
    'B05001_003E': 'naturalized_citizen',
    'B05001_006E': 'not_us_citizen',
}

# Family structure
ACS_FAMILY_VARIABLES = {
    'B11001_001E': 'family_universe',
    'B11001_002E': 'family_households',
    'B11001_003E': 'married_couple_families',
    'B11001_005E': 'single_male_families',
    'B11001_006E': 'single_female_families',
    'B11001_007E': 'non_family_households',
}

# Computer and internet access
ACS_COMPUTER_INTERNET_VARIABLES = {
    'B28001_002E': 'computer_with_broadband',
    'B28001_003E': 'computer_without_broadband',
    'B28001_005E': 'smartphone_only',
    'B28001_006E': 'no_computer',
}

# Detailed race categories
ACS_DETAILED_RACE_VARIABLES = {
    'B03002_005E': 'american_indian_alone',
    'B03002_006E': 'asian_alone',
    'B03002_007E': 'native_hawaiian_pi_alone',
    'B03002_008E': 'some_other_race_alone',
    'B03002_009E': 'two_or_more_races',
    'B03002_010E': 'two_races_including_other',
    'B03002_011E': 'two_races_excluding_other',
}

# Detailed occupation categories
ACS_OCCUPATION_DETAILED_VARIABLES = {
    'B24010_002E': 'occ_management',
    'B24010_003E': 'occ_business_financial',
    'B24010_004E': 'occ_computer_math',
    'B24010_005E': 'occ_architecture_engineering',
    'B24010_007E': 'occ_life_physical_science',
    'B24010_008E': 'occ_social_service',
    'B24010_010E': 'occ_legal',
    'B24010_011E': 'occ_education',
    'B24010_013E': 'occ_healthcare_practitioners',
    'B24010_018E': 'occ_protective_service',
    'B24010_021E': 'occ_food_prep_service',
    'B24010_022E': 'occ_building_grounds',
    'B24010_023E': 'occ_personal_care',
    'B24010_025E': 'occ_sales',
    'B24010_026E': 'occ_office_admin',
    'B24010_030E': 'occ_construction',
    'B24010_031E': 'occ_extraction',
    'B24010_032E': 'occ_installation_maintenance',
    'B24010_033E': 'occ_production',
    'B24010_036E': 'occ_transportation',
}

# Detailed industry categories
ACS_INDUSTRY_DETAILED_VARIABLES = {
    'B24050_003E': 'ind_agriculture',
    'B24050_004E': 'ind_mining',
    'B24050_005E': 'ind_utilities',
    'B24050_006E': 'ind_construction',
    'B24050_007E': 'ind_manufacturing',
    'B24050_009E': 'ind_wholesale_trade',
    'B24050_010E': 'ind_retail_trade',
    'B24050_011E': 'ind_transportation',
    'B24050_012E': 'ind_information',
    'B24050_013E': 'ind_finance_insurance',
    'B24050_014E': 'ind_real_estate',
    'B24050_015E': 'ind_professional_scientific',
    'B24050_016E': 'ind_management',
    'B24050_017E': 'ind_educational',
    'B24050_018E': 'ind_healthcare',
    'B24050_019E': 'ind_arts_entertainment',
    'B24050_020E': 'ind_accommodation_food',
    'B24050_021E': 'ind_other_services',
    'B24050_022E': 'ind_public_admin',
}

# Commute time
ACS_COMMUTE_TIME_VARIABLES = {
    'B08303_003E': 'commute_5_9_min',
    'B08303_004E': 'commute_10_14_min',
    'B08303_005E': 'commute_15_19_min',
    'B08303_006E': 'commute_20_24_min',
    'B08303_007E': 'commute_25_29_min',
    'B08303_008E': 'commute_30_34_min',
    'B08303_009E': 'commute_35_39_min',
    'B08303_010E': 'commute_40_44_min',
    'B08303_011E': 'commute_45_59_min',
    'B08303_012E': 'commute_60_89_min',
    'B08303_013E': 'commute_90plus_min',
}

# Migration/mobility
ACS_MIGRATION_VARIABLES = {
    'B07001_002E': 'same_house_1yr',
    'B07001_003E': 'moved_same_county',
    'B07001_004E': 'moved_diff_county_same_state',
    'B07001_006E': 'moved_diff_state',
    'B07001_012E': 'moved_from_abroad',
}

# Marital status
ACS_MARITAL_STATUS_VARIABLES = {
    'B12001_003E': 'never_married_male',
    'B12001_004E': 'now_married_male',
    'B12001_005E': 'separated_male',
    'B12001_006E': 'divorced_male',
    'B12001_007E': 'widowed_male',
    'B12001_011E': 'never_married_female',
    'B12001_012E': 'now_married_female',
    'B12001_013E': 'separated_female',
    'B12001_014E': 'divorced_female',
    'B12001_015E': 'widowed_female',
}

# Fertility
ACS_FERTILITY_VARIABLES = {
    'B13001_002E': 'women_with_birth_past_year',
    'B13001_009E': 'women_no_birth_past_year',
}

# Grandparents
ACS_GRANDPARENTS_VARIABLES = {
    'B10050_002E': 'grandparents_living_with_grandchildren',
    'B10050_005E': 'grandparents_responsible',
}

# Group quarters population
ACS_GROUP_QUARTERS_VARIABLES = {
    'B26001_002E': 'institutionalized',
    'B26001_003E': 'non_institutionalized',
}

# School enrollment
ACS_SCHOOL_ENROLLMENT_VARIABLES = {
    'B14001_003E': 'enrolled_nursery',
    'B14001_004E': 'enrolled_elementary',
    'B14001_005E': 'enrolled_middle_high',
    'B14001_006E': 'enrolled_college',
    'B14001_002E': 'not_enrolled',
}

# Income by source
ACS_INCOME_BY_SOURCE_VARIABLES = {
    'B19054_003E': 'income_wages_salary',
    'B19054_004E': 'income_self_employment',
    'B19054_005E': 'income_interest',
    'B19054_006E': 'income_dividends',
    'B19054_007E': 'income_rental',
    'B19054_008E': 'income_social_security',
    'B19054_009E': 'income_retirement',
    'B19054_010E': 'income_ssi',
    'B19054_011E': 'income_public_assistance',
    'B19054_012E': 'income_snap',
}

# Import configuration - enable/disable batches
IMPORT_CONFIG = {
    # Currently imported categories (enabled by default)
    'core': True,
    'age': True,
    'housing': True,
    'education': True,
    'employment': True,
    'commute': True,
    'health_insurance': True,
    'disability': True,
    'veteran': True,
    'language': True,
    'income_brackets': True,
    'housing_year_built': True,
    'housing_units': True,
    'vehicle_availability': True,
    'housing_cost_burden': True,
    'citizenship': True,
    'family': True,
    # New categories (disabled by default for incremental import)
    'computer_internet': False,
    'detailed_race': False,
    'occupation_detailed': False,
    'industry_detailed': False,
    'commute_time': False,
    'migration': False,
    'marital_status': False,
    'fertility': False,
    'grandparents': False,
    'group_quarters': False,
    'school_enrollment': False,
    'income_by_source': False,
}

# Kansas City metro area counties
KC_COUNTIES = [
    # Missouri
    ('29', '095', 'Jackson'),
    ('29', '047', 'Clay'),
    ('29', '165', 'Platte'),
    ('29', '037', 'Cass'),
    
    # Kansas
    ('20', '091', 'Johnson'),
    ('20', '209', 'Wyandotte'),
    ('20', '103', 'Leavenworth'),
    ('20', '121', 'Miami')
]

def setup_logging():
    """Setup logging"""
    logger = logging.getLogger('load_acs_data')
    logger.setLevel(logging.INFO)
    
    # File handler
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_dir / 'acs_etl.log')
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def fetch_acs_batch(state_fips, county_fips, variables_dict, logger, batch_name=""):
    """Fetch a batch of ACS variables"""
    
    if not variables_dict:
        return None
        
    # Build variable list
    vars_list = list(variables_dict.keys())
    vars_string = 'NAME,' + ','.join(vars_list)
    
    # Build API request
    params = {
        'get': vars_string,
        'for': 'block group:*',
        'in': f'state:{state_fips} county:{county_fips} tract:*'
    }
    
    # Note: Census API allows unauthenticated access with rate limits
    # For production use, register at: https://api.census.gov/data/key_signup.html
    # Then uncomment the lines below:
    # api_key = os.getenv('CENSUS_API_KEY')
    # if api_key:
    #     params['key'] = api_key
    
    try:
        logger.info(f"Fetching ACS data for state={state_fips}, county={county_fips}...")
        
        response = requests.get(ACS_BASE_URL, params=params, timeout=60)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Convert to DataFrame
        if len(data) < 2:
            logger.warning(f"No data returned for county {county_fips}")
            return None
        
        # First row is headers
        headers = data[0]
        rows = data[1:]
        
        df = pd.DataFrame(rows, columns=headers)
        
        # Build 12-digit GEOID from state + county + tract + block group
        df['GEOID'] = df['state'] + df['county'] + df['tract'] + df['block group']
        
        # Rename variables to friendly names
        rename_map = {k: variables_dict[k] for k in variables_dict.keys() if k in df.columns}
        df = df.rename(columns=rename_map)
        
        # Map total_population to population for consistency
        if 'total_population' in df.columns:
            df = df.rename(columns={'total_population': 'population'})
        
        # Convert numeric columns - use the variables_dict instead of ACS_VARIABLES
        for col in variables_dict.values():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate poverty_rate
        if 'poverty_universe' in df.columns and 'poverty_count' in df.columns:
            df['poverty_rate'] = df['poverty_count'] / df['poverty_universe']
        
        # Age group aggregation - skip for now, will fetch separately if needed
        # For now, just use median_age from B01002_001E
        
        # Add metadata
        df['acs_year'] = ACS_YEAR
        df['acs_release'] = ACS_RELEASE
        
        logger.info(f"Fetched {len(df)} block groups for county {county_fips}")
        
        # Add small delay to respect API rate limits
        time.sleep(0.2)
        
        return df
        
    except Exception as e:
        logger.error(f"Error fetching ACS data for county {county_fips}: {e}")
        return None

def load_to_database(df, logger):
    """Load ACS data into the tiger_boundaries.gpkg file"""
    
    try:
        import geopandas as gpd
        
        # Handle both single DataFrame and list of DataFrames
        if isinstance(df, list):
            logger.info(f"Received {len(df)} data batches")
            # If list, concatenate all DataFrames
            if len(df) == 0:
                logger.error("Empty list of DataFrames")
                return
            df_concat = pd.concat(df, axis=1)
            # Remove duplicate columns (GEOID, state, county, etc.)
            df_merge = df_concat.loc[:, ~df_concat.columns.duplicated()]
        else:
            df_merge = df.copy()
        
        logger.info(f"Loading {len(df_merge)} records into tiger_boundaries.gpkg...")
        
        # Path to TIGER GeoPackage
        tiger_path = project_root / "data" / "processed" / "tiger_boundaries.gpkg"
        
        if not tiger_path.exists():
            logger.error(f"TIGER boundaries file not found: {tiger_path}")
            logger.error("Please run the TIGER boundaries ETL first:")
            logger.error("  python tools/etl/load_tiger_boundaries.py")
            return
        
        # Read existing block groups
        gdf = gpd.read_file(tiger_path, layer='bg')
        
        logger.info(f"Found {len(gdf)} block groups in TIGER file")
        
        # Add ACS columns if they don't exist
        acs_columns = {
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
            'acs_year': 'object',
            'acs_release': 'object'
        }
        
        for col, dtype in acs_columns.items():
            if col not in gdf.columns:
                gdf[col] = None
                gdf[col] = gdf[col].astype(dtype)
                logger.info(f"Added column: {col}")
        
        # Merge ACS data with TIGER data
        logger.info("Merging ACS data with TIGER boundaries...")
        
        # Convert GEOID to string for proper matching
        df_merge['GEOID'] = df_merge['GEOID'].astype(str)
        gdf['GEOID'] = gdf['GEOID'].astype(str)
        
        # Merge on GEOID
        updates = 0
        for idx, acs_row in df_merge.iterrows():
            geoid = acs_row['GEOID']
            matching_idx = gdf[gdf['GEOID'] == geoid].index
            
            if len(matching_idx) > 0:
                # Update the matching row with ACS data
                for col in df_merge.columns:
                    if col not in ['GEOID', 'state', 'county', 'tract', 'block group', 'NAME']:
                        if col in gdf.columns:
                            # Check if value is not None and not 'None' string
                            val = acs_row[col]
                            if pd.notna(val) and val != 'None' and str(val).strip() != '':
                                gdf.loc[matching_idx[0], col] = acs_row[col]
                                updates += 1
        
        logger.info(f"Made {updates} field updates across {len(df_merge)} block groups")
        
        # Count updated records
        updated = 0
        for col in df_merge.columns:
            if col not in ['GEOID', 'state', 'county', 'tract', 'block group', 'NAME']:
                if col in gdf.columns:
                    count = gdf[col].notna().sum()
                    if count > updated:
                        updated = count
        
        logger.info(f"Updated {updated} block groups with ACS data")
        
        # Debug: Check a sample value before write
        if len(df_merge) > 0:
            test_geoid = df_merge.iloc[0]['GEOID']
            matching = gdf[gdf['GEOID'] == test_geoid]
            if len(matching) > 0:
                sample_col = [c for c in df_merge.columns if 'health_insurance' in c]
                if sample_col:
                    sample_val = matching.iloc[0][sample_col[0]]
                    logger.info(f"Debug: Sample value for {sample_col[0]} before write: {sample_val}")
        
        # Write back to GeoPackage
        logger.info(f"Writing updated data to {tiger_path}...")
        gdf.to_file(tiger_path, layer='bg', driver='GPKG')
        
        logger.info(f"Successfully saved ACS data to TIGER GeoPackage")
        
    except Exception as e:
        logger.error(f"Error loading data to database: {e}")
        import traceback
        traceback.print_exc()
        raise

def main():
    """Main ETL function"""
    logger = setup_logging()
    
    logger.info("Starting ACS Data ETL...")
    logger.info(f"Census API: {ACS_BASE_URL}")
    logger.info(f"ACS Year: {ACS_YEAR}")
    logger.info(f"Target counties: {len(KC_COUNTIES)}")
    
    # Check for API key
    api_key = os.getenv('CENSUS_API_KEY')
    if not api_key:
        logger.error("CENSUS_API_KEY not found in environment variables")
        logger.error("Please add it to your .env file")
        return
    
    all_data = []
    
    # Fetch data for each county
    for state_fips, county_fips, county_name in KC_COUNTIES:
        logger.info(f"\nProcessing {county_name} County (state={state_fips}, county={county_fips})...")
        
        # Collect batches for this county
        batches = []
        
        # Fetch all variable batches based on IMPORT_CONFIG
        if IMPORT_CONFIG['core']:
            core_df = fetch_acs_batch(state_fips, county_fips, ACS_CORE_VARIABLES, logger, "Core")
            if core_df is not None:
                batches.append(core_df)
        
        if IMPORT_CONFIG['age']:
            age_df = fetch_acs_batch(state_fips, county_fips, ACS_AGE_VARIABLES, logger, "Age Distribution")
            if age_df is not None:
                batches.append(age_df)
        
        if IMPORT_CONFIG['housing']:
            housing_df = fetch_acs_batch(state_fips, county_fips, ACS_HOUSING_VARIABLES, logger, "Housing")
            if housing_df is not None:
                batches.append(housing_df)
        
        if IMPORT_CONFIG['education']:
            edu_df = fetch_acs_batch(state_fips, county_fips, ACS_EDUCATION_VARIABLES, logger, "Education")
            if edu_df is not None:
                batches.append(edu_df)
        
        if IMPORT_CONFIG['employment']:
            emp_df = fetch_acs_batch(state_fips, county_fips, ACS_EMPLOYMENT_VARIABLES, logger, "Employment")
            if emp_df is not None:
                batches.append(emp_df)
        
        if IMPORT_CONFIG['commute']:
            commute_df = fetch_acs_batch(state_fips, county_fips, ACS_COMMUTE_VARIABLES, logger, "Commuting")
            if commute_df is not None:
                batches.append(commute_df)
        
        if IMPORT_CONFIG['health_insurance']:
            health_df = fetch_acs_batch(state_fips, county_fips, ACS_HEALTH_INSURANCE_VARIABLES, logger, "Health Insurance")
            if health_df is not None:
                batches.append(health_df)
        
        if IMPORT_CONFIG['disability']:
            disability_df = fetch_acs_batch(state_fips, county_fips, ACS_DISABILITY_VARIABLES, logger, "Disability")
            if disability_df is not None:
                batches.append(disability_df)
        
        if IMPORT_CONFIG['veteran']:
            veteran_df = fetch_acs_batch(state_fips, county_fips, ACS_VETERAN_VARIABLES, logger, "Veteran")
            if veteran_df is not None:
                batches.append(veteran_df)
        
        if IMPORT_CONFIG['language']:
            language_df = fetch_acs_batch(state_fips, county_fips, ACS_LANGUAGE_VARIABLES, logger, "Language")
            if language_df is not None:
                batches.append(language_df)
        
        if IMPORT_CONFIG['income_brackets']:
            income_df = fetch_acs_batch(state_fips, county_fips, ACS_INCOME_BRACKETS_VARIABLES, logger, "Income Brackets")
            if income_df is not None:
                batches.append(income_df)
        
        if IMPORT_CONFIG['housing_year_built']:
            year_df = fetch_acs_batch(state_fips, county_fips, ACS_HOUSING_YEAR_BUILT_VARIABLES, logger, "Housing Year Built")
            if year_df is not None:
                batches.append(year_df)
        
        if IMPORT_CONFIG['housing_units']:
            units_df = fetch_acs_batch(state_fips, county_fips, ACS_HOUSING_UNITS_VARIABLES, logger, "Housing Units")
            if units_df is not None:
                batches.append(units_df)
        
        if IMPORT_CONFIG['vehicle_availability']:
            vehicle_df = fetch_acs_batch(state_fips, county_fips, ACS_VEHICLE_AVAILABILITY_VARIABLES, logger, "Vehicle Availability")
            if vehicle_df is not None:
                batches.append(vehicle_df)
        
        if IMPORT_CONFIG['housing_cost_burden']:
            burden_df = fetch_acs_batch(state_fips, county_fips, ACS_HOUSING_COST_BURDEN_VARIABLES, logger, "Housing Cost Burden")
            if burden_df is not None:
                batches.append(burden_df)
        
        if IMPORT_CONFIG['citizenship']:
            citizenship_df = fetch_acs_batch(state_fips, county_fips, ACS_CITIZENSHIP_VARIABLES, logger, "Citizenship")
            if citizenship_df is not None:
                batches.append(citizenship_df)
        
        if IMPORT_CONFIG['family']:
            family_df = fetch_acs_batch(state_fips, county_fips, ACS_FAMILY_VARIABLES, logger, "Family Structure")
            if family_df is not None:
                batches.append(family_df)
        
        # New categories
        if IMPORT_CONFIG['computer_internet']:
            comp_df = fetch_acs_batch(state_fips, county_fips, ACS_COMPUTER_INTERNET_VARIABLES, logger, "Computer/Internet")
            if comp_df is not None:
                batches.append(comp_df)
        
        if IMPORT_CONFIG['detailed_race']:
            race_df = fetch_acs_batch(state_fips, county_fips, ACS_DETAILED_RACE_VARIABLES, logger, "Detailed Race")
            if race_df is not None:
                batches.append(race_df)
        
        if IMPORT_CONFIG['occupation_detailed']:
            occ_df = fetch_acs_batch(state_fips, county_fips, ACS_OCCUPATION_DETAILED_VARIABLES, logger, "Occupation Detailed")
            if occ_df is not None:
                batches.append(occ_df)
        
        if IMPORT_CONFIG['industry_detailed']:
            ind_df = fetch_acs_batch(state_fips, county_fips, ACS_INDUSTRY_DETAILED_VARIABLES, logger, "Industry Detailed")
            if ind_df is not None:
                batches.append(ind_df)
        
        if IMPORT_CONFIG['commute_time']:
            commute_time_df = fetch_acs_batch(state_fips, county_fips, ACS_COMMUTE_TIME_VARIABLES, logger, "Commute Time")
            if commute_time_df is not None:
                batches.append(commute_time_df)
        
        if IMPORT_CONFIG['migration']:
            migrate_df = fetch_acs_batch(state_fips, county_fips, ACS_MIGRATION_VARIABLES, logger, "Migration")
            if migrate_df is not None:
                batches.append(migrate_df)
        
        if IMPORT_CONFIG['marital_status']:
            marital_df = fetch_acs_batch(state_fips, county_fips, ACS_MARITAL_STATUS_VARIABLES, logger, "Marital Status")
            if marital_df is not None:
                batches.append(marital_df)
        
        if IMPORT_CONFIG['fertility']:
            fert_df = fetch_acs_batch(state_fips, county_fips, ACS_FERTILITY_VARIABLES, logger, "Fertility")
            if fert_df is not None:
                batches.append(fert_df)
        
        if IMPORT_CONFIG['grandparents']:
            gp_df = fetch_acs_batch(state_fips, county_fips, ACS_GRANDPARENTS_VARIABLES, logger, "Grandparents")
            if gp_df is not None:
                batches.append(gp_df)
        
        if IMPORT_CONFIG['group_quarters']:
            gq_df = fetch_acs_batch(state_fips, county_fips, ACS_GROUP_QUARTERS_VARIABLES, logger, "Group Quarters")
            if gq_df is not None:
                batches.append(gq_df)
        
        if IMPORT_CONFIG['school_enrollment']:
            school_df = fetch_acs_batch(state_fips, county_fips, ACS_SCHOOL_ENROLLMENT_VARIABLES, logger, "School Enrollment")
            if school_df is not None:
                batches.append(school_df)
        
        if IMPORT_CONFIG['income_by_source']:
            income_src_df = fetch_acs_batch(state_fips, county_fips, ACS_INCOME_BY_SOURCE_VARIABLES, logger, "Income by Source")
            if income_src_df is not None:
                batches.append(income_src_df)
        
        # Merge batches for this county
        if batches:
            county_combined = batches[0]
            for batch in batches[1:]:
                county_combined = county_combined.merge(batch, on='GEOID', how='outer', suffixes=('', '_dup'))
            all_data.append(county_combined)
    
    if not all_data:
        logger.error("No data fetched from Census API")
        return
    
    # Combine all counties
    logger.info("Combining data from all counties...")
    combined_df = pd.concat(all_data, ignore_index=True)
    
    logger.info(f"Total block groups: {len(combined_df)}")
    logger.info(f"Columns: {combined_df.columns.tolist()}")
    
    # Show sample statistics
    if 'population' in combined_df.columns:
        logger.info(f"Population range: {combined_df['population'].min()} - {combined_df['population'].max()}")
    if 'median_household_income' in combined_df.columns:
        income_with_values = combined_df[combined_df['median_household_income'] >= 0]
        if len(income_with_values) > 0:
            logger.info(f"Income range: ${income_with_values['median_household_income'].min():,.0f} - ${income_with_values['median_household_income'].max():,.0f}")
    
    # Load to database
    load_to_database(combined_df, logger)
    
    logger.info("\nACS Data ETL Complete!")
    logger.info(f"Total block groups processed: {len(combined_df)}")

if __name__ == "__main__":
    main()

