# Crime API Blueprint

from .base import BaseAPI
from flask import jsonify, request
from ..services.data_service import DataService
from ..services.filter_service import FilterService
from ..models.crime import CrimeIncident
from ..utils.geojson import model_to_geojson

class CrimeAPI(BaseAPI):
    """Crime incidents API endpoints"""
    
    def __init__(self):
        super().__init__('crime', __name__)
        self.data_service = DataService()
        self.filter_service = FilterService()
    
    def register_routes(self):
        """Register crime API routes"""
        
        @self.bp.route('/', methods=['GET'])
        def get_crime_incidents():
            """Get crime incidents with filtering and pagination"""
            try:
                # Parse query parameters
                bbox = self.validate_bbox(request.args.get('bbox'))
                limit = self.validate_limit(request.args.get('limit'))
                offset = self.validate_offset(request.args.get('offset'))
                
                # Parse filters
                filters = {}
                if request.args.get('offense'):
                    filters['offense'] = request.args.get('offense')
                if request.args.get('district'):
                    filters['district'] = request.args.get('district')
                if request.args.get('date_from'):
                    filters['date_from'] = request.args.get('date_from')
                if request.args.get('date_to'):
                    filters['date_to'] = request.args.get('date_to')
                
                # Get features
                if bbox:
                    features = self.data_service.get_features_by_bbox(
                        CrimeIncident, bbox, limit, offset, **filters
                    )
                else:
                    features = self.data_service.get_features(
                        CrimeIncident, limit, offset, **filters
                    )
                
                # Convert to GeoJSON
                geojson_features = []
                for feature in features:
                    geojson_feature = model_to_geojson(feature, 'crime')
                    if geojson_feature:
                        geojson_features.append(geojson_feature)
                
                return jsonify({
                    'type': 'FeatureCollection',
                    'features': geojson_features,
                    'metadata': {
                        'layer': 'crime',
                        'count': len(geojson_features),
                        'limit': limit,
                        'offset': offset
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/stats', methods=['GET'])
        def get_crime_stats():
            """Get crime statistics"""
            try:
                bbox = self.validate_bbox(request.args.get('bbox'))
                
                stats = self.data_service.get_aggregated_stats(
                    CrimeIncident, 'offense', bbox
                )
                
                return jsonify({
                    'stats': stats,
                    'metadata': {
                        'layer': 'crime',
                        'bbox': bbox
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/filters', methods=['GET'])
        def get_filter_options():
            """Get available filter options for crime data"""
            try:
                options = self.filter_service.get_filter_options(CrimeIncident)
                
                return jsonify({
                    'filters': options,
                    'metadata': {
                        'layer': 'crime'
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
