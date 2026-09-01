# Combined API Blueprint

from .base import BaseAPI
from flask import jsonify, request
from ..services.data_service import DataService
from ..services.consolidation_service import ConsolidationService
from ..services.filter_service import FilterService

class CombinedAPI(BaseAPI):
    """Combined multi-dataset consolidated API endpoints"""
    
    def __init__(self):
        super().__init__('combined', __name__)
        self.data_service = DataService()
        self.consolidation_service = ConsolidationService()
        self.filter_service = FilterService()
    
    def register_routes(self):
        """Register combined API routes"""
        
        @self.bp.route('/features', methods=['GET'])
        def get_consolidated_features():
            """Get consolidated features across all layers"""
            try:
                # Parse query parameters
                bbox = self.validate_bbox(request.args.get('bbox'))
                limit = self.validate_limit(request.args.get('limit'))
                
                if not bbox:
                    return jsonify({'error': 'bbox parameter required'}), 400
                
                # Get requested layers
                layers_param = request.args.get('layers', 'service_requests,crime,points')
                requested_layers = [l.strip() for l in layers_param.split(',')]
                
                # Parse filters for each layer
                layer_filters = self.filter_service.parse_layer_filters(request, requested_layers)
                
                # Get features from all requested layers
                all_features = {}
                for layer in requested_layers:
                    filters = layer_filters.get(layer, {})
                    features = self.data_service.get_layer_features(layer, bbox, limit, filters)
                    if features:
                        all_features[layer] = features
                
                # Apply cross-layer consolidation
                consolidated_features = self.consolidation_service.aggregate_cross_layer_features(all_features)
                
                # Calculate source counts for each layer
                source_counts = {}
                for layer_name, features in all_features.items():
                    source_counts[layer_name] = len(features)
                
                return jsonify({
                    'type': 'FeatureCollection',
                    'features': consolidated_features,
                    'metadata': {
                        'consolidated': True,
                        'cross_layer': True,
                        'count': len(consolidated_features),
                        'source_layers': list(all_features.keys()),
                        'source_counts': source_counts
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/stats', methods=['GET'])
        def get_combined_stats():
            """Get combined statistics across all layers"""
            try:
                bbox = self.validate_bbox(request.args.get('bbox'))
                
                if not bbox:
                    return jsonify({'error': 'bbox parameter required'}), 400
                
                # Get layer info for all layers
                layer_info = self.data_service.get_all_layer_info(bbox)
                
                return jsonify({
                    'layer_info': layer_info,
                    'metadata': {
                        'bbox': bbox,
                        'consolidated': True
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
