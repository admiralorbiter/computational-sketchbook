"""
Business API Blueprint

Provides REST API endpoints for business data.
"""

from flask import Blueprint, request, jsonify
from web.services.data_service import DataService
from web.services.filter_service import FilterService
from web.models.business import Business
import logging

logger = logging.getLogger(__name__)

class BusinessAPI:
    """Business API endpoints"""
    
    def __init__(self):
        self.bp = Blueprint('businesses', __name__)
        self.data_service = DataService()
        self.filter_service = FilterService()
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes"""
        
        @self.bp.route('/', methods=['GET'])
        def get_businesses():
            """Get businesses within bounding box"""
            try:
                # Get query parameters
                bbox_param = request.args.get('bbox')
                if not bbox_param:
                    return jsonify({"error": "bbox parameter required"}), 400
                
                try:
                    bbox = [float(x) for x in bbox_param.split(',')]
                    if len(bbox) != 4:
                        raise ValueError("bbox must have 4 coordinates")
                except ValueError as e:
                    return jsonify({"error": f"Invalid bbox format: {e}"}), 400
                
                limit = request.args.get('limit', 2000, type=int)
                offset = request.args.get('offset', 0, type=int)
                
                # Parse filters
                filters = {}
                if request.args.get('business_type'):
                    filters['business_type'] = request.args.get('business_type')
                if request.args.get('source'):
                    filters['source'] = request.args.get('source')
                if request.args.get('industry'):
                    filters['industry'] = request.args.get('industry')
                if request.args.get('search_text'):
                    filters['search_text'] = request.args.get('search_text')
                
                # Get features
                features = self.data_service.get_features_by_bbox(
                    Business, bbox, limit, offset, **filters
                )
                
                # Convert to GeoJSON
                geojson_features = []
                for business in features:
                    geojson_feature = self._convert_to_geojson(business)
                    if geojson_feature:
                        geojson_features.append(geojson_feature)
                
                return jsonify({
                    "type": "FeatureCollection",
                    "features": geojson_features,
                    "metadata": {
                        "layer": "businesses",
                        "count": len(geojson_features),
                        "limit": limit,
                        "offset": offset
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting businesses: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.bp.route('/filters', methods=['GET'])
        def get_filters():
            """Get available filter options for businesses"""
            try:
                filters = self.filter_service.get_business_filter_options()
                return jsonify({
                    'filters': filters,
                    'metadata': {
                        'layer': 'businesses'
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting business filters: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.bp.route('/stats', methods=['GET'])
        def get_stats():
            """Get business statistics"""
            try:
                # Get query parameters
                bbox_param = request.args.get('bbox')
                bbox = None
                if bbox_param:
                    try:
                        bbox = [float(x) for x in bbox_param.split(',')]
                        if len(bbox) != 4:
                            raise ValueError("bbox must have 4 coordinates")
                    except ValueError as e:
                        return jsonify({"error": f"Invalid bbox format: {e}"}), 400
                
                # Get stats
                stats = {}
                
                # Total count
                if bbox:
                    features = self.data_service.get_features_by_bbox(Business, bbox, limit=10000)
                    stats['total'] = len(features)
                else:
                    session = self.data_service.get_db_session()
                    try:
                        stats['total'] = session.query(Business).count()
                    finally:
                        session.close()
                
                # Count by source
                source_stats = self.data_service.get_aggregated_stats(Business, 'source', bbox)
                stats['by_source'] = {item['value']: item['count'] for item in source_stats}
                
                # Count by business type
                type_stats = self.data_service.get_aggregated_stats(Business, 'business_type', bbox)
                stats['by_type'] = {item['value']: item['count'] for item in type_stats}
                
                return jsonify({
                    'stats': stats,
                    'metadata': {
                        'layer': 'businesses',
                        'bbox': bbox
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting business stats: {e}")
                return jsonify({"error": str(e)}), 500
    
    def _convert_to_geojson(self, business):
        """Convert Business model to GeoJSON feature"""
        try:
            if not business.latitude or not business.longitude:
                return None
            
            properties = {
                'id': business.id,
                'type': 'businesses',  # Add type field for frontend compatibility
                'name': business.name,
                'business_type': business.business_type,
                'address': business.address,
                'city': business.city,
                'state': business.state,
                'zipcode': business.zipcode,
                'source': business.source,
                'description': business.description,
                'industry': business.industry
            }
            
            # Add source-specific fields
            if business.source == 'license':
                properties.update({
                    'dba_name': business.dba_name,
                    'valid_license_for': business.valid_license_for
                })
            elif business.source == 'company':
                properties.update({
                    'place_id': business.place_id,
                    'place_type': business.place_type
                })
            
            geometry = {
                'type': 'Point',
                'coordinates': [business.longitude, business.latitude]
            }
            
            return {
                'type': 'Feature',
                'properties': properties,
                'geometry': geometry
            }
            
        except Exception as e:
            logger.error(f"Error converting business to GeoJSON: {e}")
            return None
