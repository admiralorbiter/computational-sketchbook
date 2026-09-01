# Spatial Service

import sqlite3
from shapely import wkb
from shapely.geometry import mapping
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SpatialService:
    """Service for spatial operations and geometry handling"""
    
    def __init__(self):
        # OSM database path
        from pathlib import Path
        self.osm_database_path = str(Path(__file__).parent.parent.parent / "data" / "processed" / "missouri.gpkg")
    
    def parse_wkb_to_geojson(self, wkb_blob):
        """Parse WKB blob to GeoJSON geometry - handles both WKB and GeoPackage formats"""
        try:
            if not wkb_blob:
                return None
            
            # Check if it's GeoPackage format (starts with 'GP')
            if wkb_blob.startswith(b'GP'):
                # GeoPackage format - try different header sizes
                for header_size in [8, 4, 0]:
                    try:
                        wkb_data = wkb_blob[header_size:]
                        geom = wkb.loads(wkb_data)
                        return mapping(geom)
                    except:
                        continue
                return None
            else:
                # Standard WKB format
                geom = wkb.loads(wkb_blob)
                return mapping(geom)
        except Exception as e:
            logger.error(f"Error parsing geometry: {e}")
            return None
    
    def extract_coordinates_from_geom(self, geom_blob):
        """Extract coordinates from geometry blob for legacy compatibility"""
        try:
            if not geom_blob:
                return None
            
            # Use the existing parse_wkb_to_geojson function
            return self.parse_wkb_to_geojson(geom_blob)
        except Exception as e:
            logger.error(f"Error extracting coordinates: {e}")
            return None
    
    def validate_bbox(self, bbox):
        """Validate bounding box format and values"""
        if not bbox or len(bbox) != 4:
            return False
        
        minx, miny, maxx, maxy = bbox
        
        # Check that min < max for both dimensions
        if minx >= maxx or miny >= maxy:
            return False
        
        # Check reasonable coordinate ranges (rough bounds for continental US)
        if not (-180 <= minx <= 180) or not (-180 <= maxx <= 180):
            return False
        if not (-90 <= miny <= 90) or not (-90 <= maxy <= 90):
            return False
        
        return True
    
    def get_osm_features(self, layer, bbox, limit, filter_type=None):
        """Get OSM features with optional consolidation for points"""
        try:
            conn = sqlite3.connect(self.osm_database_path)
            cursor = conn.cursor()
            
            minx, miny, maxx, maxy = bbox
            
            # Build the query based on layer type
            if layer == 'points':
                table_name = 'points'
            elif layer == 'lines':
                table_name = 'lines'
            elif layer == 'multipolygons':
                table_name = 'multipolygons'
            else:
                return []
            
            # Base query using R-tree index for spatial filtering
            query = f"""
            SELECT osm_id, name, other_tags, geom
            FROM {table_name}
            WHERE geom IS NOT NULL
            AND fid IN (
                SELECT id FROM rtree_{table_name}_geom 
                WHERE minx <= ? AND maxx >= ? 
                AND miny <= ? AND maxy >= ?
            )
            """
            
            params = [maxx, minx, maxy, miny]  # R-tree expects (maxx, minx, maxy, miny)
            
            # Add legacy filter if specified
            if filter_type:
                if filter_type == 'highway':
                    query += " AND other_tags LIKE '%highway%'"
                elif filter_type == 'building':
                    query += " AND other_tags LIKE '%building%'"
                elif filter_type == 'amenity':
                    query += " AND other_tags LIKE '%amenity%'"
                elif filter_type == 'shop':
                    query += " AND other_tags LIKE '%shop%'"
            
            query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            logger.info(f"OSM {layer} query returned {len(rows)} rows")
            
            features = []
            for row in rows:
                osm_id, name, other_tags, geom_blob = row
                
                # Parse geometry using the updated function
                geom_data = self.parse_wkb_to_geojson(geom_blob)
                if not geom_data:
                    logger.warning(f"Failed to parse geometry for OSM ID {osm_id}")
                    continue
                
                # Parse other_tags
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
                
                # Add name to tags if available
                if name:
                    tags['name'] = name
                
                # Create feature
                feature = {
                    "type": "Feature",
                    "properties": {
                        "osm_id": osm_id,
                        "type": layer,
                        "tags": tags
                    },
                    "geometry": geom_data
                }
                features.append(feature)
            
            conn.close()
            return features
            
        except Exception as e:
            logger.error(f"Error getting OSM features: {e}")
            return []
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        import math
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in meters
        r = 6371000
        return c * r
    
    def is_point_in_bbox(self, lat, lng, bbox):
        """Check if a point is within a bounding box"""
        minx, miny, maxx, maxy = bbox
        return minx <= lng <= maxx and miny <= lat <= maxy
    
    def is_point_in_radius(self, lat, lng, center_lat, center_lng, radius_meters):
        """Check if a point is within a radius of another point"""
        distance = self.calculate_distance(lat, lng, center_lat, center_lng)
        return distance <= radius_meters
