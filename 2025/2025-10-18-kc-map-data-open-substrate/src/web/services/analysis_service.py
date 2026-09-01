"""
Analysis Service

Provides methods for analyzing block groups with comprehensive data breakdowns.
"""

import sqlite3
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for block group analysis and aggregations"""
    
    def __init__(self):
        from web.config import config
        current_config = config['development']
        self.database_url = current_config.DATABASE_URL
        self.tiger_database_path = str(Path(__file__).parent.parent.parent / "data" / "processed" / "tiger_boundaries.gpkg")
        
        # Initialize employment service
        try:
            from web.services.employment_service import EmploymentService
            self.employment_service = EmploymentService()
        except Exception as e:
            logger.warning(f"Could not initialize employment service: {e}")
            self.employment_service = None
    
    def get_block_group_analysis(self, geoid: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get comprehensive analysis for a specific block group
        
        Args:
            geoid: Block group GEOID
            filters: Optional filters to apply
            
        Returns:
            Dictionary containing ACS data, aggregations, and breakdowns
        """
        try:
            # Load block group geometry and ACS data from TIGER boundaries
            block_group_data = self._load_block_group_from_tiger(geoid)
            
            if not block_group_data:
                return {"error": "Block group not found"}
            
            # Load aggregations from main database
            aggregations = self._load_aggregations(geoid)
            
            # Load employment data (LODES)
            employment_data = self._get_employment_data(geoid)
            
            # Combine data
            result = {
                "geoid": geoid,
                "name": block_group_data.get('name'),
                "acs": block_group_data,  # Include all ACS data
                "aggregations": {
                    "crime_total": aggregations.get('total_crime_incidents', 0),
                    "crime_by_offense": self._parse_json_field(aggregations.get('crime_by_offense')),
                    "sr_total": aggregations.get('total_311_requests', 0),
                    "sr_by_issue_type": self._parse_json_field(aggregations.get('sr_by_issue_type')),
                    "businesses_total": aggregations.get('total_businesses', 0),
                    "business_by_type": self._parse_json_field(aggregations.get('business_by_type')),
                    "business_by_industry": self._parse_json_field(aggregations.get('business_by_industry')),
                    "dangerous_buildings": aggregations.get('total_dangerous_buildings', 0),
                    "landbank_properties": aggregations.get('total_landbank_properties', 0)
                },
                "geometry": block_group_data.get('geometry')
            }
            
            # Add employment data if available
            if employment_data:
                result['employment'] = employment_data
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting block group analysis: {e}")
            return {"error": str(e)}
    
    def get_detailed_breakdown(self, geoid: str, data_type: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get detailed breakdown for specific data type
        
        Args:
            geoid: Block group GEOID
            data_type: 'crime', '311', 'businesses', etc.
            filters: Optional filters
            
        Returns:
            Detailed breakdown
        """
        aggregations = self._load_aggregations(geoid)
        
        if data_type == 'crime':
            return {
                "total": aggregations.get('total_crime_incidents', 0),
                "breakdown": self._parse_json_field(aggregations.get('crime_by_offense'))
            }
        elif data_type == '311':
            return {
                "total": aggregations.get('total_311_requests', 0),
                "breakdown": self._parse_json_field(aggregations.get('sr_by_issue_type'))
            }
        elif data_type == 'businesses':
            return {
                "total": aggregations.get('total_businesses', 0),
                "breakdown_by_type": self._parse_json_field(aggregations.get('business_by_type')),
                "breakdown_by_industry": self._parse_json_field(aggregations.get('business_by_industry'))
            }
        else:
            return {"error": "Unknown data type"}
    
    def _load_block_group_from_tiger(self, geoid: str) -> Optional[Dict[str, Any]]:
        """Load block group data from TIGER boundaries GeoPackage"""
        try:
            import geopandas as gpd
            
            gdf = gpd.read_file(self.tiger_database_path, layer='bg')
            block_group = gdf[gdf['GEOID'] == geoid]
            
            if len(block_group) == 0:
                return None
            
            row = block_group.iloc[0]
            
            # Extract geometry as GeoJSON
            geometry = row['geometry'].__geo_interface__
            
            # Helper function to clean and convert values
            def get_value(col_name, default=None):
                val = row.get(col_name)
                # Handle NaN, None, or empty string
                if pd.isna(val) or val is None or val == '':
                    return default
                # Convert to string first to handle numeric strings
                try:
                    val_str = str(val).strip()
                    if val_str == 'nan' or val_str == '' or val_str == 'None':
                        return default
                    # Try to convert to int
                    return int(float(val_str))
                except (ValueError, TypeError) as e:
                    logger.debug(f"Could not convert {col_name} value '{val}' to int: {e}")
                    return default
            
            def get_float(col_name, default=None):
                val = row.get(col_name)
                if pd.isna(val) or val is None or val == '':
                    return default
                try:
                    val_str = str(val).strip()
                    if val_str == 'nan' or val_str == '':
                        return default
                    return float(val_str)
                except (ValueError, TypeError) as e:
                    logger.debug(f"Could not convert {col_name} value '{val}' to float: {e}")
                    return default
            
            # Build result - comprehensive ACS data
            result = {
                'name': f"Block Group {row.get('NAMELSAD', geoid)}",
                'geometry': geometry,
                # Basic Demographics
                'population': get_value('population'),
                'median_household_income': get_value('median_household_income'),
                'median_age': get_float('median_age'),
                'poverty_rate': get_float('poverty_rate'),
                # Race & Ethnicity
                'white_alone': get_value('white_alone'),
                'black_alone': get_value('black_alone'),
                'hispanic_latino': get_value('hispanic_latino'),
                'total_race': get_value('total_race'),
                # Age Distribution
                'male_under_18': get_value('male_under_5', 0) + get_value('male_5_9', 0) + get_value('male_10_14', 0) + get_value('male_15_17', 0),
                'female_under_18': get_value('female_under_5', 0) + get_value('female_5_9', 0) + get_value('female_10_14', 0) + get_value('female_15_17', 0),
                'male_18_64': sum([get_value(f'male_{key}', 0) for key in ['18_19', '20', '21', '22_24', '25_29', '30_34', '35_39', '40_44', '45_49', '50_54', '55_59', '60_61', '62_64']]),
                'female_18_64': sum([get_value(f'female_{key}', 0) for key in ['18_19', '20', '21', '22_24', '25_29', '30_34', '35_39', '40_44', '45_49', '50_54', '55_59', '60_61', '62_64']]),
                'male_65_plus': sum([get_value(f'male_{key}', 0) for key in ['65_66', '67_69', '70_74', '75_79', '80_84', '85_over']]),
                'female_65_plus': sum([get_value(f'female_{key}', 0) for key in ['65_66', '67_69', '70_74', '75_79', '80_84', '85_over']]),
                # Housing
                'housing_occupied': get_value('housing_occupied'),
                'housing_vacant': get_value('housing_vacant'),
                'owner_occupied': get_value('owner_occupied'),
                'renter_occupied': get_value('renter_occupied'),
                'total_housing_units': get_value('total_housing_units'),
                'median_home_value': get_value('median_home_value'),
                'median_rent': get_value('median_rent'),
                'homeownership_rate': get_float('homeownership_rate'),
                'vacancy_rate': get_float('vacancy_rate'),
                # Education
                'education_universe': get_value('education_universe'),
                'high_school_grad': get_value('high_school_grad'),
                'bachelors_degree': get_value('bachelors_degree'),
                'masters_degree': get_value('masters_degree'),
                'professional_degree': get_value('professional_degree'),
                'doctorate_degree': get_value('doctorate_degree'),
                'bachelors_plus_pct': get_float('bachelors_plus_pct'),
                # Employment
                'employment_universe': get_value('employment_universe'),
                'in_labor_force': get_value('in_labor_force'),
                'employed': get_value('employed'),
                'unemployed': get_value('unemployed'),
                'employment_rate': get_float('employment_rate'),
                'unemployment_rate': get_float('unemployment_rate'),
                # Commuting
                'commute_universe': get_value('commute_universe'),
                'drove_alone': get_value('drove_alone'),
                'carpooled': get_value('carpooled'),
                'public_transit': get_value('public_transit'),
                'walked': get_value('walked'),
                'bicycle': get_value('bicycle'),
                'work_from_home': get_value('work_from_home'),
                'transit_pct': get_float('transit_pct'),
                'remote_work_pct': get_float('remote_work_pct'),
                # Vehicle Availability
                'no_vehicles': get_value('no_vehicles'),
                'one_vehicle': get_value('one_vehicle'),
                'two_vehicles': get_value('two_vehicles'),
                'three_vehicles': get_value('three_vehicles'),
                'four_or_more_vehicles': get_value('four_or_more_vehicles'),
                # Income Distribution
                'income_less_10000': get_value('income_less_10000'),
                'income_10000_14999': get_value('income_10000_14999'),
                'income_15000_19999': get_value('income_15000_19999'),
                'income_20000_24999': get_value('income_20000_24999'),
                'income_25000_29999': get_value('income_25000_29999'),
                'income_30000_34999': get_value('income_30000_34999'),
                'income_35000_39999': get_value('income_35000_39999'),
                'income_40000_44999': get_value('income_40000_44999'),
                'income_45000_49999': get_value('income_45000_49999'),
                'income_50000_59999': get_value('income_50000_59999'),
                'income_60000_74999': get_value('income_60000_74999'),
                'income_75000_99999': get_value('income_75000_99999'),
                'income_100000_124999': get_value('income_100000_124999'),
                'income_125000_149999': get_value('income_125000_149999'),
                'income_150000_199999': get_value('income_150000_199999'),
                'income_200000_or_more': get_value('income_200000_or_more'),
                # Housing Year Built
                'built_2014_later': get_value('built_2014_later'),
                'built_2010_2013': get_value('built_2010_2013'),
                'built_2000_2009': get_value('built_2000_2009'),
                'built_1990_1999': get_value('built_1990_1999'),
                'built_1980_1989': get_value('built_1980_1989'),
                'built_1970_1979': get_value('built_1970_1979'),
                'built_1960_1969': get_value('built_1960_1969'),
                'built_1950_1959': get_value('built_1950_1959'),
                'built_1940_1949': get_value('built_1940_1949'),
                'built_1939_or_earlier': get_value('built_1939_or_earlier'),
                # Housing Unit Types
                'single_unit_detached': get_value('single_unit_detached'),
                'single_unit_attached': get_value('single_unit_attached'),
                'units_2_4': get_value('units_2_4'),
                'units_5_9': get_value('units_5_9'),
                'units_10_19': get_value('units_10_19'),
                'units_20_49': get_value('units_20_49'),
                'units_50_or_more': get_value('units_50_or_more'),
                'mobile_home': get_value('mobile_home'),
                # Family Structure
                'family_households': get_value('family_households'),
                'married_couple_families': get_value('married_couple_families'),
                'single_male_families': get_value('single_male_families'),
                'single_female_families': get_value('single_female_families'),
                'non_family_households': get_value('non_family_households'),
                # Housing Cost Burden
                'housing_cost_less_20pct': get_value('housing_cost_less_20pct'),
                'housing_cost_20_24pct': get_value('housing_cost_20_24pct'),
                'housing_cost_25_29pct': get_value('housing_cost_25_29pct'),
                'housing_cost_30_34pct': get_value('housing_cost_30_34pct'),
                'housing_cost_35pct_or_more': get_value('housing_cost_35pct_or_more'),
                # Citizenship
                'native_born': get_value('native_born'),
                'naturalized_citizen': get_value('naturalized_citizen'),
                'not_us_citizen': get_value('not_us_citizen'),
                # Computer/Internet Access (NEW)
                'computer_with_broadband': get_value('computer_with_broadband'),
                'computer_without_broadband': get_value('computer_without_broadband'),
                'smartphone_only': get_value('smartphone_only'),
                'no_computer': get_value('no_computer'),
                # Detailed Race (NEW)
                'american_indian_alone': get_value('american_indian_alone'),
                'asian_alone': get_value('asian_alone'),
                'native_hawaiian_pi_alone': get_value('native_hawaiian_pi_alone'),
                'some_other_race_alone': get_value('some_other_race_alone'),
                'two_or_more_races': get_value('two_or_more_races'),
                # Migration (NEW)
                'same_house_1yr': get_value('same_house_1yr'),
                'moved_same_county': get_value('moved_same_county'),
                'moved_diff_county_same_state': get_value('moved_diff_county_same_state'),
                'moved_diff_state': get_value('moved_diff_state'),
                'moved_from_abroad': get_value('moved_from_abroad'),
                # Grandparents (NEW)
                'grandparents_living_with_grandchildren': get_value('grandparents_living_with_grandchildren'),
                'grandparents_responsible': get_value('grandparents_responsible'),
                # School Enrollment (NEW)
                'enrolled_nursery': get_value('enrolled_nursery'),
                'enrolled_elementary': get_value('enrolled_elementary'),
                'enrolled_middle_high': get_value('enrolled_middle_high'),
                'enrolled_college': get_value('enrolled_college'),
                'not_enrolled': get_value('not_enrolled'),
                # Commute Time (NEW)
                'commute_5_9_min': get_value('commute_5_9_min'),
                'commute_10_14_min': get_value('commute_10_14_min'),
                'commute_15_19_min': get_value('commute_15_19_min'),
                'commute_20_24_min': get_value('commute_20_24_min'),
                'commute_25_29_min': get_value('commute_25_29_min'),
                'commute_30_34_min': get_value('commute_30_34_min'),
                'commute_35_39_min': get_value('commute_35_39_min'),
                'commute_40_44_min': get_value('commute_40_44_min'),
                'commute_45_59_min': get_value('commute_45_59_min'),
                'commute_60_89_min': get_value('commute_60_89_min'),
                'commute_90plus_min': get_value('commute_90plus_min'),
                # Health Insurance (NEW)
                'health_insurance_universe': get_value('health_insurance_universe'),
                'with_health_insurance': get_value('with_health_insurance'),
                'with_private_insurance': get_value('with_private_insurance'),
                'with_public_insurance': get_value('with_public_insurance'),
                'without_health_insurance': get_value('without_health_insurance'),
                # Disability (NEW)
                'disability_universe': get_value('disability_universe'),
                'with_disability': get_value('with_disability'),
                'without_disability': get_value('without_disability'),
                # Veteran Status (NEW)
                'veteran_universe': get_value('veteran_universe'),
                'veteran_status_with_flag': get_value('veteran_status_with_flag'),
                'veteran_status_without_flag': get_value('veteran_status_without_flag'),
                # Language (NEW)
                'language_universe': get_value('language_universe'),
                'english_only': get_value('english_only'),
                'spanish_speak_limited_english': get_value('spanish_speak_limited_english'),
                'other_language_speak_limited_english': get_value('other_language_speak_limited_english'),
                # Citizenship Universe (NEW)
                'nativity_universe': get_value('nativity_universe'),
                # Income by Source (if available)
                'income_wages_salary': get_value('income_wages_salary'),
                'income_self_employment': get_value('income_self_employment'),
                'income_interest': get_value('income_interest'),
                'income_dividends': get_value('income_dividends'),
                'income_rental': get_value('income_rental'),
                'income_retirement': get_value('income_retirement'),
                'income_social_security': get_value('income_social_security'),
                'income_ssi': get_value('income_ssi'),
                'income_public_assistance': get_value('income_public_assistance'),
                'income_snap': get_value('income_snap'),
                # Housing Bedrooms (if available)
                'owner_bedrooms_0': get_value('owner_bedrooms_0'),
                'owner_bedrooms_1': get_value('owner_bedrooms_1'),
                'owner_bedrooms_2': get_value('owner_bedrooms_2'),
                'owner_bedrooms_3plus': get_value('owner_bedrooms_3plus'),
                'renter_bedrooms_0': get_value('renter_bedrooms_0'),
                'renter_bedrooms_1': get_value('renter_bedrooms_1'),
                'renter_bedrooms_2': get_value('renter_bedrooms_2'),
                'renter_bedrooms_3plus': get_value('renter_bedrooms_3plus'),
                # Internet Subscriptions (if available)
                'internet_subscription_cable': get_value('internet_subscription_cable'),
                'internet_subscription_dsl': get_value('internet_subscription_dsl'),
                'internet_subscription_fiber': get_value('internet_subscription_fiber'),
                'internet_subscription_dialup': get_value('internet_subscription_dialup'),
                'internet_subscription_satellite': get_value('internet_subscription_satellite'),
                'internet_subscription_cellular': get_value('internet_subscription_cellular'),
                # Housing Cost Burden Universe
                'cost_burden_universe': get_value('cost_burden_universe'),
                # Vehicle Universe
                'vehicle_universe': get_value('vehicle_universe'),
                # Family Universe
                'family_universe': get_value('family_universe'),
                # Group Quarters (if available)
                'group_quarters_total': get_value('group_quarters_total'),
                'institutionalized': get_value('institutionalized'),
                'non_institutionalized': get_value('non_institutionalized'),
                # Age aggregates we calculated
                'youth': get_value('youth'),
                'working_age': get_value('working_age'),
                'seniors': get_value('seniors'),
                'youth_pct': get_float('youth_pct'),
                'working_age_pct': get_float('working_age_pct'),
                'seniors_pct': get_float('seniors_pct')
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error loading block group from TIGER: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _load_aggregations(self, geoid: str) -> Dict[str, Any]:
        """Load pre-computed aggregations from database"""
        try:
            import sqlite3
            
            db_path = self.database_url.replace('sqlite:///', '')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    total_crime_incidents,
                    total_311_requests,
                    total_businesses,
                    total_dangerous_buildings,
                    total_landbank_properties,
                    crime_by_offense,
                    sr_by_issue_type,
                    business_by_type,
                    business_by_industry
                FROM block_group_aggregations
                WHERE geoid = ?
            """, (geoid,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return {}
            
            return {
                'total_crime_incidents': row[0],
                'total_311_requests': row[1],
                'total_businesses': row[2],
                'total_dangerous_buildings': row[3],
                'total_landbank_properties': row[4],
                'crime_by_offense': row[5],
                'sr_by_issue_type': row[6],
                'business_by_type': row[7],
                'business_by_industry': row[8]
            }
            
        except Exception as e:
            logger.error(f"Error loading aggregations: {e}")
            return {}
    
    def _get_employment_data(self, geoid: str) -> Optional[Dict[str, Any]]:
        """Get LODES employment data for a block group"""
        if not self.employment_service:
            return None
        
        try:
            return self.employment_service.get_block_group_employment(geoid)
        except Exception as e:
            logger.warning(f"Could not load employment data for {geoid}: {e}")
            return None
    
    def _parse_json_field(self, json_str: Optional[str]) -> dict:
        """Parse JSON string field safely"""
        if not json_str:
            return {}
        
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return {}

