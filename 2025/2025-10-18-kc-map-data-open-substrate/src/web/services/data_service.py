"""
Data Service

Handles database access and query operations for all data sources.
Provides a clean interface between the API layer and database models.
"""

import sqlite3
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, or_
from ..config import config
from ..models.base import Base
from ..models.crime import CrimeIncident
from ..models.service_requests import ServiceRequest
from ..models.business import Business
from ..models.dangerous_buildings import DangerousBuilding
from ..models.landbank import LandBankProperty
from ..models.census import BlockGroup, Block
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DataService:
    """Data access service for database operations"""
    
    def __init__(self):
        # Get current config
        current_config = config['development']  # TODO: Make configurable
        self.database_url = current_config.DATABASE_URL
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Legacy OSM database path
        self.osm_database_path = str(Path(__file__).parent.parent.parent / "data" / "processed" / "missouri.gpkg")
        
        # TIGER boundaries database path
        self.tiger_database_path = str(Path(__file__).parent.parent.parent / "data" / "processed" / "tiger_boundaries.gpkg")
    
    def get_db_session(self):
        """Get database session for KC data"""
        return self.Session()
    
    def get_osm_connection(self):
        """Get connection to OSM database"""
        return sqlite3.connect(self.osm_database_path)
    
    def get_tiger_connection(self):
        """Get connection to TIGER boundaries database"""
        return sqlite3.connect(self.tiger_database_path)
    
    def get_census_features(self, layer_name, bbox, simplify=0):
        """Get Census boundary features with bbox filtering
        
        Args:
            layer_name: 'block_groups' or 'blocks'
            bbox: [minx, miny, maxx, maxy] bounding box
            simplify: Optional simplification in meters (0 = no simplification)
        
        Returns:
            List of GeoJSON features
        """
        try:
            import geopandas as gpd
            from shapely.geometry import box
            
            # Map layer name to GeoPackage layer name
            gpkg_layer_name = 'bg' if layer_name == 'block_groups' else 'tabblock20'
            
            # Debug: Check if layer exists
            logger.debug(f"Looking for layer: {gpkg_layer_name}")
            
            # Filter by bounding box BEFORE reading from GeoPackage for better performance
            try:
                minx, miny, maxx, maxy = bbox
                # Use spatial index to filter efficiently
                gdf = gpd.read_file(
                    self.tiger_database_path, 
                    layer=gpkg_layer_name,
                    bbox=(minx, miny, maxx, maxy)  # Pass bbox to read_file for spatial filtering
                )
                logger.info(f"Loaded {len(gdf)} features from {gpkg_layer_name} layer (bbox filtered)")
            except Exception as e:
                logger.error(f"Error reading layer {gpkg_layer_name}: {e}")
                return []
            
            # Apply simplification if requested
            if simplify > 0:
                # Simplify in Web Mercator so "meters" make sense
                gdf = gdf.to_crs(3857)  # Web Mercator
                gdf['geometry'] = gdf.geometry.simplify(simplify, preserve_topology=True)
                gdf = gdf.to_crs(4326)  # Back to WGS84
            
            # ACS data is now directly in the GeoPackage, no need to join
            acs_lookup = {}
            
            # Convert to GeoJSON features
            features = []
            for idx, row in gdf.iterrows():
                geoid = row.get('GEOID', row.get('GEOID10'))
                
                # Helper to clean NaN values for JSON serialization
                import math
                import pandas as pd
                
                def clean_value(val):
                    if val is None:
                        return None
                    # Convert numpy/pandas types to Python native types
                    import numpy as np
                    if isinstance(val, (np.integer, np.int64)):
                        return int(val)
                    if isinstance(val, (np.floating, np.float64)):
                        if math.isnan(val) or math.isinf(val):
                            return None
                        return float(val)
                    # Check for pandas NaT, NaN
                    try:
                        if pd.isna(val):
                            return None
                    except (TypeError, ValueError):
                        pass
                    # Check for float NaN
                    if isinstance(val, float):
                        try:
                            if math.isnan(val) or math.isinf(val):
                                return None
                        except (TypeError, ValueError):
                            pass
                    # Check for string representations of NaN
                    if isinstance(val, str) and (val.lower() in ['nan', 'none', 'int64', 'float64', 'float', 'int', 'nat']):
                        return None
                    return val
                
                feature = {
                    'type': 'Feature',
                    'geometry': row.geometry.__geo_interface__,
                    'properties': {
                        'geoid': geoid,
                        'state': row.get('STATEFP'),
                        'county': row.get('COUNTYFP'),
                        'name': row.get('NAMELSAD', row.get('NAME'))
                    }
                }
                
                # Add all other TIGER attributes to properties (clean NaN values)
                for col in row.index:
                    if col not in ['geometry']:
                        feature['properties'][col] = clean_value(row[col])
                
                # Add ACS data if available (already cleaned in lookup)
                if geoid in acs_lookup:
                    feature['properties'].update(acs_lookup[geoid])
                
                features.append(feature)
            
            return features
            
        except Exception as e:
            logger.error(f"Error getting Census features: {e}")
            return []
    
    def get_features_by_bbox(self, model_class, bbox, limit=2000, offset=0, **filters):
        """Get features within bounding box"""
        session = self.get_db_session()
        try:
            minx, miny, maxx, maxy = bbox
            
            query = session.query(model_class).filter(
                model_class.latitude.isnot(None),
                model_class.longitude.isnot(None),
                model_class.latitude >= miny,
                model_class.latitude <= maxy,
                model_class.longitude >= minx,
                model_class.longitude <= maxx
            )
            
            # Apply additional filters
            for key, value in filters.items():
                if hasattr(model_class, key) and value is not None:
                    if key == 'search_text':
                        # Handle text search across multiple fields
                        search_terms = value.split()
                        search_conditions = []
                        for term in search_terms:
                            term_conditions = []
                            if hasattr(model_class, 'name'):
                                term_conditions.append(model_class.name.ilike(f'%{term}%'))
                            if hasattr(model_class, 'address'):
                                term_conditions.append(model_class.address.ilike(f'%{term}%'))
                            if hasattr(model_class, 'business_type'):
                                term_conditions.append(model_class.business_type.ilike(f'%{term}%'))
                            if hasattr(model_class, 'industry'):
                                term_conditions.append(model_class.industry.ilike(f'%{term}%'))
                            if term_conditions:
                                search_conditions.append(or_(*term_conditions))
                        if search_conditions:
                            query = query.filter(and_(*search_conditions))
                    elif isinstance(value, str) and ',' in value:
                        # Handle multi-value filters (comma-separated)
                        values = [v.strip() for v in value.split(',')]
                        query = query.filter(getattr(model_class, key).in_(values))
                    else:
                        # Handle single value filters
                        query = query.filter(getattr(model_class, key) == value)
            
            return query.offset(offset).limit(limit).all()
        finally:
            session.close()
    
    def get_features(self, model_class, limit=2000, offset=0, **filters):
        """Get features with filters (no spatial constraint)"""
        session = self.get_db_session()
        try:
            query = session.query(model_class)
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(model_class, key) and value is not None:
                    query = query.filter(getattr(model_class, key) == value)
            
            return query.offset(offset).limit(limit).all()
        finally:
            session.close()
    
    def get_layer_features(self, layer_name, bbox, limit=2000, filters=None):
        """Get features for a specific layer (handles both KC data and OSM)"""
        if layer_name in ['service_requests', 'crime', 'businesses', 'dangerous_buildings', 'landbank_properties']:
            # KC data using SQLAlchemy
            if layer_name == 'service_requests':
                model_class = ServiceRequest
            elif layer_name == 'crime':
                model_class = CrimeIncident
            elif layer_name == 'businesses':
                model_class = Business
            elif layer_name == 'dangerous_buildings':
                model_class = DangerousBuilding
            elif layer_name == 'landbank_properties':
                model_class = LandBankProperty
            
            # Apply filters properly
            session = self.get_db_session()
            try:
                minx, miny, maxx, maxy = bbox
                
                query = session.query(model_class).filter(
                    model_class.latitude.isnot(None),
                    model_class.longitude.isnot(None),
                    model_class.latitude >= miny,
                    model_class.latitude <= maxy,
                    model_class.longitude >= minx,
                    model_class.longitude <= maxx
                )
                
                # Apply filters if provided
                if filters:
                    if layer_name == 'service_requests' and 'issue_type' in filters:
                        if isinstance(filters['issue_type'], list):
                            query = query.filter(model_class.issue_type.in_(filters['issue_type']))
                        else:
                            query = query.filter(model_class.issue_type == filters['issue_type'])
                    elif layer_name == 'crime' and 'offense_type' in filters:
                        if isinstance(filters['offense_type'], list):
                            query = query.filter(model_class.offense.in_(filters['offense_type']))
                        else:
                            query = query.filter(model_class.offense == filters['offense_type'])
                    elif layer_name == 'businesses':
                        if 'business_type' in filters:
                            if isinstance(filters['business_type'], list):
                                query = query.filter(model_class.business_type.in_(filters['business_type']))
                            else:
                                query = query.filter(model_class.business_type == filters['business_type'])
                        if 'source' in filters:
                            if isinstance(filters['source'], list):
                                query = query.filter(model_class.source.in_(filters['source']))
                            else:
                                query = query.filter(model_class.source == filters['source'])
                        if 'industry' in filters:
                            if isinstance(filters['industry'], list):
                                query = query.filter(model_class.industry.in_(filters['industry']))
                            else:
                                query = query.filter(model_class.industry == filters['industry'])
                    elif layer_name == 'dangerous_buildings':
                        if 'status_of_case' in filters:
                            if isinstance(filters['status_of_case'], list):
                                query = query.filter(model_class.status_of_case.in_(filters['status_of_case']))
                            else:
                                query = query.filter(model_class.status_of_case == filters['status_of_case'])
                        if 'council_district' in filters:
                            if isinstance(filters['council_district'], list):
                                query = query.filter(model_class.council_district.in_(filters['council_district']))
                            else:
                                query = query.filter(model_class.council_district == filters['council_district'])
                    elif layer_name == 'landbank_properties':
                        if 'property_status' in filters:
                            if isinstance(filters['property_status'], list):
                                query = query.filter(model_class.property_status.in_(filters['property_status']))
                            else:
                                query = query.filter(model_class.property_status == filters['property_status'])
                        if 'inventory_type' in filters:
                            if isinstance(filters['inventory_type'], list):
                                query = query.filter(model_class.inventory_type.in_(filters['inventory_type']))
                            else:
                                query = query.filter(model_class.inventory_type == filters['inventory_type'])
                        if 'neighborhood' in filters:
                            if isinstance(filters['neighborhood'], list):
                                query = query.filter(model_class.neighborhood.in_(filters['neighborhood']))
                            else:
                                query = query.filter(model_class.neighborhood == filters['neighborhood'])
                        if 'city_council_district' in filters:
                            if isinstance(filters['city_council_district'], list):
                                query = query.filter(model_class.city_council_district.in_(filters['city_council_district']))
                            else:
                                query = query.filter(model_class.city_council_district == filters['city_council_district'])
                        if 'property_class' in filters:
                            if isinstance(filters['property_class'], list):
                                query = query.filter(model_class.property_class.in_(filters['property_class']))
                            else:
                                query = query.filter(model_class.property_class == filters['property_class'])
                        if 'property_condition' in filters:
                            if isinstance(filters['property_condition'], list):
                                query = query.filter(model_class.property_condition.in_(filters['property_condition']))
                            else:
                                query = query.filter(model_class.property_condition == filters['property_condition'])
                        if 'demo_needed' in filters:
                            query = query.filter(model_class.demo_needed == filters['demo_needed'])
                        if 'search_text' in filters:
                            search_term = f"%{filters['search_text']}%"
                            query = query.filter(
                                or_(
                                    model_class.address.ilike(search_term),
                                    model_class.parcel_number.ilike(search_term)
                                )
                            )
                
                features = query.limit(limit).all()
                return [self._convert_kc_to_geojson(f, layer_name) for f in features]
            finally:
                session.close()
        
        elif layer_name == 'points':
            # OSM data using legacy SQLite
            return self._get_osm_features('points', bbox, limit, filters)
        
        return []
    
    def get_aggregated_stats(self, model_class, group_by, bbox=None):
        """Get aggregated statistics"""
        session = self.get_db_session()
        try:
            query = session.query(
                getattr(model_class, group_by),
                session.query(model_class.id).count().label('count')
            )
            
            if bbox:
                minx, miny, maxx, maxy = bbox
                query = query.filter(
                    and_(
                        model_class.longitude >= minx,
                        model_class.longitude <= maxx,
                        model_class.latitude >= miny,
                        model_class.latitude <= maxy
                    )
                )
            
            results = query.group_by(getattr(model_class, group_by)).all()
            return [{'value': value, 'count': count} for value, count in results]
        finally:
            session.close()
    
    def get_all_layer_info(self, bbox=None):
        """Get information about all layers"""
        layers = {}
        
        # Get KC data layer info
        try:
            session = self.get_db_session()
            
            # Service requests
            sr_count = session.query(ServiceRequest).count()
            layers['service_requests'] = {
                'name': '311 Service Requests',
                'count': sr_count,
                'type': 'kc_data'
            }
            
            # Crime incidents
            crime_count = session.query(CrimeIncident).count()
            layers['crime'] = {
                'name': 'Crime Incidents',
                'count': crime_count,
                'type': 'kc_data'
            }
            
            # Businesses
            business_count = session.query(Business).count()
            layers['businesses'] = {
                'name': 'Businesses',
                'count': business_count,
                'type': 'kc_data'
            }
            
            # Dangerous Buildings
            dangerous_count = session.query(DangerousBuilding).count()
            layers['dangerous_buildings'] = {
                'name': 'Dangerous Buildings',
                'count': dangerous_count,
                'type': 'kc_data'
            }
            
            # Land Bank Properties
            landbank_count = session.query(LandBankProperty).count()
            layers['landbank_properties'] = {
                'name': 'Land Bank Properties',
                'count': landbank_count,
                'type': 'kc_data'
            }
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error getting KC layer info: {e}")
            layers['service_requests'] = {'name': '311 Service Requests', 'count': 0, 'type': 'kc_data'}
            layers['crime'] = {'name': 'Crime Incidents', 'count': 0, 'type': 'kc_data'}
            layers['businesses'] = {'name': 'Businesses', 'count': 0, 'type': 'kc_data'}
            layers['dangerous_buildings'] = {'name': 'Dangerous Buildings', 'count': 0, 'type': 'kc_data'}
            layers['landbank_properties'] = {'name': 'Land Bank Properties', 'count': 0, 'type': 'kc_data'}
        
        # Get TIGER boundaries layer info
        try:
            import geopandas as gpd
            tiger_path = Path(self.tiger_database_path)
            if tiger_path.exists():
                # Get block groups count
                bg_gdf = gpd.read_file(self.tiger_database_path, layer='bg')
                layers['block_groups'] = {
                    'name': 'Block Groups',
                    'count': len(bg_gdf),
                    'type': 'census'
                }
                
                # Get blocks count
                blocks_gdf = gpd.read_file(self.tiger_database_path, layer='tabblock20')
                layers['blocks'] = {
                    'name': 'Blocks',
                    'count': len(blocks_gdf),
                    'type': 'census'
                }
            else:
                layers['block_groups'] = {'name': 'Block Groups', 'count': 0, 'type': 'census'}
                layers['blocks'] = {'name': 'Blocks', 'count': 0, 'type': 'census'}
        except Exception as e:
            logger.error(f"Error getting TIGER layer info: {e}")
            layers['block_groups'] = {'name': 'Block Groups', 'count': 0, 'type': 'census'}
            layers['blocks'] = {'name': 'Blocks', 'count': 0, 'type': 'census'}
        
        # Get OSM layer info
        try:
            conn = self.get_osm_connection()
            cursor = conn.cursor()
            
            for layer in ['points']:  # Only points for now
                cursor.execute(f"SELECT COUNT(*) FROM {layer}")
                count = cursor.fetchone()[0]
                layers[layer] = {
                    'name': layer.title(),
                    'count': count,
                    'type': 'osm'
                }
            
            conn.close()
        except Exception as e:
            logger.error(f"Error getting OSM layer info: {e}")
            layers['points'] = {'name': 'Points', 'count': 0, 'type': 'osm'}
        
        return layers
    
    def _convert_kc_to_geojson(self, item, layer_type):
        """Convert KC data item to GeoJSON feature"""
        try:
            properties = {
                'id': item.id,
                'type': layer_type
            }
            
            # Add layer-specific properties
            if layer_type == 'crime':
                properties.update({
                    'report': getattr(item, 'report', None),
                    'offense': getattr(item, 'offense', None),
                    'address': getattr(item, 'address', None),
                    'latitude': getattr(item, 'latitude', None),
                    'longitude': getattr(item, 'longitude', None)
                })
            elif layer_type == 'service_requests':
                properties.update({
                    'request_id': getattr(item, 'request_id', None),
                    'issue_type': getattr(item, 'issue_type', None),
                    'current_status': getattr(item, 'current_status', None),
                    'incident_address': getattr(item, 'incident_address', None),
                    'latitude': getattr(item, 'latitude', None),
                    'longitude': getattr(item, 'longitude', None)
                })
            elif layer_type == 'businesses':
                properties.update({
                    'name': getattr(item, 'name', None),
                    'business_type': getattr(item, 'business_type', None),
                    'address': getattr(item, 'address', None),
                    'city': getattr(item, 'city', None),
                    'state': getattr(item, 'state', None),
                    'source': getattr(item, 'source', None),
                    'description': getattr(item, 'description', None),
                    'industry': getattr(item, 'industry', None),
                    'latitude': getattr(item, 'latitude', None),
                    'longitude': getattr(item, 'longitude', None)
                })
            elif layer_type == 'dangerous_buildings':
                properties.update({
                    'case_number': getattr(item, 'case_number', None),
                    'address': getattr(item, 'address', None),
                    'city': getattr(item, 'city', None),
                    'state': getattr(item, 'state', None),
                    'zipcode': getattr(item, 'zipcode', None),
                    'case_opened': getattr(item, 'case_opened', None),
                    'status_of_case': getattr(item, 'status_of_case', None),
                    'pin': getattr(item, 'pin', None),
                    'council_district': getattr(item, 'council_district', None),
                    'latitude': getattr(item, 'latitude', None),
                    'longitude': getattr(item, 'longitude', None)
                })
            elif layer_type == 'landbank_properties':
                properties.update({
                    'address': getattr(item, 'address', None),
                    'city': getattr(item, 'city', None),
                    'state': getattr(item, 'state', None),
                    'postal_code': getattr(item, 'postal_code', None),
                    'parcel_number': getattr(item, 'parcel_number', None),
                    'property_status': getattr(item, 'property_status', None),
                    'inventory_type': getattr(item, 'inventory_type', None),
                    'property_class': getattr(item, 'property_class', None),
                    'property_condition': getattr(item, 'property_condition', None),
                    'market_value': getattr(item, 'market_value', None),
                    'market_value_year': getattr(item, 'market_value_year', None),
                    'square_footage': getattr(item, 'square_footage', None),
                    'demo_needed': getattr(item, 'demo_needed', None),
                    'city_council_district': getattr(item, 'city_council_district', None),
                    'county': getattr(item, 'county', None),
                    'neighborhood': getattr(item, 'neighborhood', None),
                    'school_district': getattr(item, 'school_district', None),
                    'zoned_as': getattr(item, 'zoned_as', None),
                    'date_of_acquisition': getattr(item, 'date_of_acquisition', None),
                    'latitude': getattr(item, 'latitude', None),
                    'longitude': getattr(item, 'longitude', None)
                })
            
            geometry = {
                'type': 'Point',
                'coordinates': [item.longitude, item.latitude]
            }
            
            return {
                'type': 'Feature',
                'properties': properties,
                'geometry': geometry
            }
        except Exception as e:
            logger.error(f"Error converting KC item to GeoJSON: {e}")
            return None
    
    def _get_osm_features(self, layer, bbox, limit, filters=None):
        """Get OSM features (legacy compatibility)"""
        try:
            conn = self.get_osm_connection()
            cursor = conn.cursor()
            
            minx, miny, maxx, maxy = bbox
            
            query = f"""
            SELECT osm_id, name, other_tags, geom
            FROM {layer}
            WHERE geom IS NOT NULL
            AND fid IN (
                SELECT id FROM rtree_{layer}_geom 
                WHERE minx <= ? AND maxx >= ? 
                AND miny <= ? AND maxy >= ?
            )
            LIMIT {limit}
            """
            
            cursor.execute(query, [maxx, minx, maxy, miny])
            rows = cursor.fetchall()
            
            features = []
            for row in rows:
                osm_id, name, other_tags, geom_blob = row
                
                # Parse geometry (simplified - would need full WKB parsing)
                # For now, return basic structure
                feature = {
                    "type": "Feature",
                    "properties": {
                        "osm_id": osm_id,
                        "type": layer,
                        "name": name,
                        "tags": self._parse_osm_tags(other_tags)
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [0, 0]  # Would extract from geom_blob
                    }
                }
                features.append(feature)
            
            conn.close()
            return features
            
        except Exception as e:
            logger.error(f"Error getting OSM features: {e}")
            return []
    
    def _parse_osm_tags(self, other_tags):
        """Parse OSM other_tags string into dictionary"""
        tags = {}
        if other_tags:
            # Parse the other_tags string format
            tag_pairs = other_tags.split('","')
            for pair in tag_pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    key = key.strip('"')
                    value = value.strip('"')
                    tags[key] = value
        return tags
