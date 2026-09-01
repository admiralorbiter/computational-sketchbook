#!/usr/bin/env python3
"""
Compute Block Group Aggregations

Performs spatial joins to compute aggregations of crime, 311, businesses,
and other data types by block group using GeoPackage spatial capabilities.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from web.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_block_groups():
    """Load all block groups from TIGER boundaries"""
    tiger_db = str(project_root / "data" / "processed" / "tiger_boundaries.gpkg")
    
    if not os.path.exists(tiger_db):
        logger.error(f"TIGER boundaries database not found: {tiger_db}")
        return None
    
    try:
        gdf = gpd.read_file(tiger_db, layer='bg')
        logger.info(f"Loaded {len(gdf)} block groups from TIGER boundaries")
        return gdf
    except Exception as e:
        logger.error(f"Error loading block groups: {e}")
        return None


def get_all_crime_incidents():
    """Load all crime incidents from main database"""
    current_config = config['development']
    db_url = current_config.DATABASE_URL
    
    try:
        from sqlalchemy import create_engine
        from web.models.crime import CrimeIncident
        
        engine = create_engine(db_url)
        query = """
        SELECT id, latitude, longitude, offense, report
        FROM crime_incidents
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """
        
        df = pd.read_sql(query, engine)
        logger.info(f"Loaded {len(df)} crime incidents with coordinates")
        
        # Convert to GeoDataFrame
        geometry = [Point(lon, lat) for lon, lat in zip(df['longitude'], df['latitude'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
        
        return gdf
    except Exception as e:
        logger.error(f"Error loading crime incidents: {e}")
        return None


def get_all_service_requests():
    """Load all 311 service requests from main database"""
    current_config = config['development']
    db_url = current_config.DATABASE_URL
    
    try:
        from sqlalchemy import create_engine
        
        engine = create_engine(db_url)
        query = """
        SELECT id, latitude, longitude, issue_type, request_id
        FROM service_requests_311
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """
        
        df = pd.read_sql(query, engine)
        logger.info(f"Loaded {len(df)} service requests with coordinates")
        
        # Convert to GeoDataFrame
        geometry = [Point(lon, lat) for lon, lat in zip(df['longitude'], df['latitude'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
        
        return gdf
    except Exception as e:
        logger.error(f"Error loading service requests: {e}")
        return None


def get_all_businesses():
    """Load all businesses from main database"""
    current_config = config['development']
    db_url = current_config.DATABASE_URL
    
    try:
        from sqlalchemy import create_engine
        
        engine = create_engine(db_url)
        query = """
        SELECT id, latitude, longitude, business_type, industry, name
        FROM businesses
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """
        
        df = pd.read_sql(query, engine)
        logger.info(f"Loaded {len(df)} businesses with coordinates")
        
        # Convert to GeoDataFrame
        geometry = [Point(lon, lat) for lon, lat in zip(df['longitude'], df['latitude'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
        
        return gdf
    except Exception as e:
        logger.error(f"Error loading businesses: {e}")
        return None


def spatial_join_features(block_groups_gdf, features_gdf, group_by_field=None):
    """Perform spatial join between block groups and features"""
    if features_gdf is None or len(features_gdf) == 0:
        return {}
    
    # Ensure same CRS
    features_gdf = features_gdf.to_crs(block_groups_gdf.crs)
    
    # Spatial join
    joined = gpd.sjoin(features_gdf, block_groups_gdf, how='inner', predicate='within')
    
    results = {}
    
    for geoid, group in joined.groupby('GEOID'):
        if group_by_field and group_by_field in joined.columns:
            # Create breakdown by field
            breakdown = group[group_by_field].value_counts().to_dict()
            results[geoid] = {
                'total': len(group),
                'breakdown': breakdown
            }
        else:
            results[geoid] = {'total': len(group)}
    
    return results


def compute_all_aggregations():
    """Compute all aggregations for all block groups"""
    
    logger.info("Starting block group aggregation computation...")
    
    # Load block groups
    block_groups = get_block_groups()
    if block_groups is None:
        return False
    
    # Initialize results
    all_results = {}
    
    # Get GEOIDs
    geoids = block_groups['GEOID'].tolist()
    logger.info(f"Processing {len(geoids)} block groups")
    
    # Load all features
    logger.info("Loading crime incidents...")
    crime_gdf = get_all_crime_incidents()
    
    logger.info("Loading service requests...")
    sr_gdf = get_all_service_requests()
    
    logger.info("Loading businesses...")
    business_gdf = get_all_businesses()
    
    # Iterate through each block group
    for idx, row in block_groups.iterrows():
        geoid = row['GEOID']
        block_group_geom = row['geometry']
        
        if idx % 100 == 0:
            logger.info(f"Processing block group {idx+1}/{len(block_groups)}: {geoid}")
        
        results = {
            'total_crime_incidents': 0,
            'total_311_requests': 0,
            'total_businesses': 0,
            'total_dangerous_buildings': 0,
            'total_landbank_properties': 0,
            'crime_by_offense': {},
            'sr_by_issue_type': {},
            'business_by_type': {},
            'business_by_industry': {}
        }
        
        # Count crime incidents
        if crime_gdf is not None and len(crime_gdf) > 0:
            crime_in_bg = crime_gdf[crime_gdf.within(block_group_geom)]
            results['total_crime_incidents'] = len(crime_in_bg)
            if 'offense' in crime_in_bg.columns:
                results['crime_by_offense'] = crime_in_bg['offense'].value_counts().to_dict()
        
        # Count service requests
        if sr_gdf is not None and len(sr_gdf) > 0:
            sr_in_bg = sr_gdf[sr_gdf.within(block_group_geom)]
            results['total_311_requests'] = len(sr_in_bg)
            if 'issue_type' in sr_in_bg.columns:
                results['sr_by_issue_type'] = sr_in_bg['issue_type'].value_counts().to_dict()
        
        # Count businesses
        if business_gdf is not None and len(business_gdf) > 0:
            business_in_bg = business_gdf[business_gdf.within(block_group_geom)]
            results['total_businesses'] = len(business_in_bg)
            if 'business_type' in business_in_bg.columns:
                results['business_by_type'] = business_in_bg['business_type'].value_counts().to_dict()
            if 'industry' in business_in_bg.columns:
                results['business_by_industry'] = business_in_bg['industry'].value_counts().to_dict()
        
        # TODO: Add dangerous buildings and landbank properties counts
        
        all_results[geoid] = results
    
    # Save to database
    logger.info("Saving results to database...")
    save_aggregations(all_results)
    
    logger.info("Aggregation computation complete!")
    return True


def save_aggregations(results):
    """Save computed aggregations to database"""
    current_config = config['development']
    db_path = current_config.DATABASE_URL.replace('sqlite:///', '')
    
    conn = None
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for geoid, data in results.items():
            # Convert dicts to JSON strings
            crime_by_offense = json.dumps(data.get('crime_by_offense', {}))
            sr_by_issue_type = json.dumps(data.get('sr_by_issue_type', {}))
            business_by_type = json.dumps(data.get('business_by_type', {}))
            business_by_industry = json.dumps(data.get('business_by_industry', {}))
            
            cursor.execute("""
            INSERT OR REPLACE INTO block_group_aggregations 
            (geoid, total_crime_incidents, total_311_requests, total_businesses,
             crime_by_offense, sr_by_issue_type, business_by_type, business_by_industry,
             last_computed, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                geoid,
                data.get('total_crime_incidents', 0),
                data.get('total_311_requests', 0),
                data.get('total_businesses', 0),
                crime_by_offense,
                sr_by_issue_type,
                business_by_type,
                business_by_industry
            ))
        
        conn.commit()
        logger.info(f"Saved {len(results)} aggregation records")
        
    except Exception as e:
        logger.error(f"Error saving aggregations: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    success = compute_all_aggregations()
    sys.exit(0 if success else 1)

