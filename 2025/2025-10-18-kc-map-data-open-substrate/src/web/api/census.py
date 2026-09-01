# Census TIGER Boundaries API Blueprint

from .base import BaseAPI
from flask import jsonify, request
from ..services.data_service import DataService

class CensusAPI(BaseAPI):
    """Census TIGER boundary data API endpoints"""
    
    def __init__(self):
        super().__init__('census', __name__)
        self.data_service = DataService()
    
    def register_routes(self):
        """Register Census API routes"""
        
        @self.bp.route('/block_groups', methods=['GET'])
        def get_block_groups():
            """Get block group features with optional bbox and simplify params"""
            try:
                bbox = self.validate_bbox(request.args.get('bbox'))
                simplify = float(request.args.get('simplify', 0))
                
                if not bbox:
                    return jsonify({'error': 'bbox parameter required'}), 400
                
                features = self.data_service.get_census_features('block_groups', bbox, simplify)
                
                return jsonify({
                    'type': 'FeatureCollection',
                    'features': features,
                    'metadata': {
                        'layer': 'block_groups',
                        'count': len(features),
                        'simplified': simplify > 0
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/blocks', methods=['GET'])
        def get_blocks():
            """Get block features with optional bbox and simplify params"""
            try:
                bbox = self.validate_bbox(request.args.get('bbox'))
                simplify = float(request.args.get('simplify', 0))
                
                if not bbox:
                    return jsonify({'error': 'bbox parameter required'}), 400
                
                features = self.data_service.get_census_features('blocks', bbox, simplify)
                
                return jsonify({
                    'type': 'FeatureCollection',
                    'features': features,
                    'metadata': {
                        'layer': 'blocks',
                        'count': len(features),
                        'simplified': simplify > 0
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500

