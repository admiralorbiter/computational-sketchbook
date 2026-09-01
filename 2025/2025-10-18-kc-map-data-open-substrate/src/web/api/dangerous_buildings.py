# Dangerous Buildings API Blueprint

from .base import BaseAPI
from flask import jsonify, request
from ..services.data_service import DataService
from ..services.filter_service import FilterService
from ..models.dangerous_buildings import DangerousBuilding
from ..utils.geojson import model_to_geojson

class DangerousBuildingsAPI(BaseAPI):
    """Dangerous Buildings API endpoints"""
    
    def __init__(self):
        super().__init__('dangerous_buildings', __name__)
        self.data_service = DataService()
        self.filter_service = FilterService()
    
    def register_routes(self):
        """Register dangerous buildings API routes"""
        
        @self.bp.route('/', methods=['GET'])
        def get_dangerous_buildings():
            """Get dangerous buildings with filtering and pagination"""
            try:
                # Parse query parameters
                bbox = self.validate_bbox(request.args.get('bbox'))
                limit = self.validate_limit(request.args.get('limit'))
                
                if not bbox:
                    return jsonify({'error': 'bbox parameter required'}), 400
                
                # Parse filters
                filters = {}
                if request.args.get('status_of_case'):
                    filters['status_of_case'] = request.args.get('status_of_case')
                if request.args.get('council_district'):
                    filters['council_district'] = request.args.get('council_district')
                if request.args.get('search_text'):
                    filters['search_text'] = request.args.get('search_text')
                
                # Get features
                features = self.data_service.get_layer_features(
                    'dangerous_buildings', bbox, limit, filters
                )
                
                return jsonify({
                    'type': 'FeatureCollection',
                    'features': features,
                    'metadata': {
                        'layer': 'dangerous_buildings',
                        'count': len(features)
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/filters', methods=['GET'])
        def get_filter_options():
            """Get available filter options for dangerous buildings"""
            try:
                options = self.filter_service.get_filter_options(DangerousBuilding)
                return jsonify({
                    'filters': options,
                    'metadata': {
                        'layer': 'dangerous_buildings'
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
