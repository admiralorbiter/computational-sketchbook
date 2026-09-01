# OSM API Blueprint

from .base import BaseAPI
from flask import jsonify, request
from ..services.spatial_service import SpatialService
from ..services.filter_service import FilterService

class OSMAPI(BaseAPI):
    """OpenStreetMap data API endpoints (legacy compatibility)"""
    
    def __init__(self):
        super().__init__('osm', __name__)
        self.spatial_service = SpatialService()
        self.filter_service = FilterService()
    
    def register_routes(self):
        """Register OSM API routes"""
        
        @self.bp.route('/<layer>', methods=['GET'])
        def get_osm_features(layer):
            """Get OSM features for specified layer"""
            try:
                # Validate layer
                if layer not in ['points', 'lines', 'multipolygons']:
                    return jsonify({'error': 'Invalid layer. Must be: points, lines, or multipolygons'}), 400
                
                # Parse query parameters
                bbox = self.validate_bbox(request.args.get('bbox'))
                limit = self.validate_limit(request.args.get('limit'))
                filter_type = request.args.get('filter')
                
                if not bbox:
                    return jsonify({'error': 'bbox parameter required'}), 400
                
                # Get features from OSM database
                features = self.spatial_service.get_osm_features(
                    layer, bbox, limit, filter_type
                )
                
                return jsonify({
                    'type': 'FeatureCollection',
                    'features': features,
                    'metadata': {
                        'layer': layer,
                        'type': 'osm',
                        'count': len(features),
                        'deprecated': 'This endpoint will be migrated to unified database'
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/<layer>/filters', methods=['GET'])
        def get_filter_options(layer):
            """Get available filter options for OSM layer"""
            try:
                if layer not in ['points', 'lines', 'multipolygons']:
                    return jsonify({'error': 'Invalid layer'}), 400
                
                options = self.filter_service.get_osm_filter_options(layer)
                
                return jsonify({
                    'filters': options,
                    'metadata': {
                        'layer': layer,
                        'type': 'osm'
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
