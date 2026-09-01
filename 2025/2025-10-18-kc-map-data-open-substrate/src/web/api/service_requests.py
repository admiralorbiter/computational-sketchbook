# Service Requests (311) API Blueprint

from .base import BaseAPI
from flask import jsonify, request
from ..services.data_service import DataService
from ..services.filter_service import FilterService
from ..models.service_requests import ServiceRequest
from ..utils.geojson import model_to_geojson

class ServiceRequestsAPI(BaseAPI):
    """311 Service Requests API endpoints"""
    
    def __init__(self):
        super().__init__('service_requests', __name__)
        self.data_service = DataService()
        self.filter_service = FilterService()
    
    def register_routes(self):
        """Register service requests API routes"""
        
        @self.bp.route('/', methods=['GET'])
        def get_service_requests():
            """Get 311 service requests with filtering and pagination"""
            try:
                # Parse query parameters
                bbox = self.validate_bbox(request.args.get('bbox'))
                limit = self.validate_limit(request.args.get('limit'))
                offset = self.validate_offset(request.args.get('offset'))
                
                # Parse filters
                filters = {}
                if request.args.get('issue_type'):
                    filters['issue_type'] = request.args.get('issue_type')
                if request.args.get('status'):
                    filters['status'] = request.args.get('status')
                if request.args.get('date_from'):
                    filters['date_from'] = request.args.get('date_from')
                if request.args.get('date_to'):
                    filters['date_to'] = request.args.get('date_to')
                
                # Get features
                if bbox:
                    features = self.data_service.get_features_by_bbox(
                        ServiceRequest, bbox, limit, offset, **filters
                    )
                else:
                    features = self.data_service.get_features(
                        ServiceRequest, limit, offset, **filters
                    )
                
                # Convert to GeoJSON
                geojson_features = []
                for feature in features:
                    geojson_feature = model_to_geojson(feature, 'service_requests')
                    if geojson_feature:
                        geojson_features.append(geojson_feature)
                
                return jsonify({
                    'type': 'FeatureCollection',
                    'features': geojson_features,
                    'metadata': {
                        'layer': 'service_requests',
                        'count': len(geojson_features),
                        'limit': limit,
                        'offset': offset
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/stats', methods=['GET'])
        def get_service_requests_stats():
            """Get 311 service requests statistics"""
            try:
                bbox = self.validate_bbox(request.args.get('bbox'))
                
                stats = self.data_service.get_aggregated_stats(
                    ServiceRequest, 'issue_type', bbox
                )
                
                return jsonify({
                    'stats': stats,
                    'metadata': {
                        'layer': 'service_requests',
                        'bbox': bbox
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/filters', methods=['GET'])
        def get_filter_options():
            """Get available filter options for 311 data"""
            try:
                options = self.filter_service.get_filter_options(ServiceRequest)
                
                return jsonify({
                    'filters': options,
                    'metadata': {
                        'layer': 'service_requests'
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
