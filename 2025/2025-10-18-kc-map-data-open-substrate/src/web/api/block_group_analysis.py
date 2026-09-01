# Block Group Analysis API Blueprint

from .base import BaseAPI
from flask import jsonify, request
from ..services.analysis_service import AnalysisService
from ..services.data_service import DataService
import logging

logger = logging.getLogger(__name__)


class BlockGroupAnalysisAPI(BaseAPI):
    """Block group analysis API endpoints"""
    
    def __init__(self):
        super().__init__('block_group_analysis', __name__)
        self.analysis_service = AnalysisService()
        self.data_service = DataService()
    
    def register_routes(self):
        """Register block group analysis API routes"""
        
        @self.bp.route('/block_groups/<geoid>', methods=['GET'])
        def get_block_group_analysis(geoid):
            """Get comprehensive analysis for a specific block group"""
            try:
                result = self.analysis_service.get_block_group_analysis(geoid)
                
                if 'error' in result:
                    return jsonify(result), 404
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error in get_block_group_analysis: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/block_groups/<geoid>/breakdown', methods=['GET'])
        def get_block_group_breakdown(geoid):
            """Get detailed breakdown for a specific block group and data type"""
            try:
                data_type = request.args.get('type')
                
                if not data_type:
                    return jsonify({'error': 'type parameter required'}), 400
                
                result = self.analysis_service.get_detailed_breakdown(geoid, data_type)
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error in get_block_group_breakdown: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/block_groups/batch', methods=['POST'])
        def get_batch_analysis():
            """Get analysis for multiple block groups"""
            try:
                data = request.get_json()
                
                if not data or 'geoids' not in data:
                    return jsonify({'error': 'geoids array required'}), 400
                
                geoids = data['geoids']
                results = {}
                
                for geoid in geoids:
                    result = self.analysis_service.get_block_group_analysis(geoid)
                    results[geoid] = result
                
                return jsonify(results)
                
            except Exception as e:
                logger.error(f"Error in get_batch_analysis: {e}")
                return jsonify({'error': str(e)}), 500

