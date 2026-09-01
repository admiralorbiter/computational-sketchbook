#!/usr/bin/env python3
"""
Geocoding API Endpoints

REST API endpoints for the geocoding service.
"""

import os
import logging
from flask import Blueprint, request, jsonify, current_app
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.geocoding.geocoding_service import GeocodingService

# Create blueprint
geocoding_bp = Blueprint('geocoding', __name__, url_prefix='/api/geocoding')

# Initialize geocoding service (lazy loading)
_geocoding_service = None

def get_geocoding_service():
    """Get or create geocoding service instance"""
    global _geocoding_service
    
    if _geocoding_service is None:
        # Get database path from config
        db_path = current_app.config['DATABASE_URL'].replace('sqlite:///', '')
        if not db_path.startswith('/'):
            # Relative path, make it absolute
            db_path = str(project_root / db_path)
        
        # Get Google API key
        google_api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
        
        # Create service
        _geocoding_service = GeocodingService(db_path, google_api_key)
    
    return _geocoding_service

@geocoding_bp.route('/geocode', methods=['POST'])
def geocode_address():
    """Geocode a single address"""
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'success': False,
                'error': 'Address is required'
            }), 400
        
        address = data['address']
        source_priority = data.get('source_priority', ['census', 'google'])
        
        # Geocode address
        service = get_geocoding_service()
        result = service.geocode_address(address, source_priority)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error geocoding address: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@geocoding_bp.route('/batch', methods=['POST'])
def batch_geocode():
    """Geocode multiple addresses"""
    try:
        data = request.get_json()
        
        if not data or 'addresses' not in data:
            return jsonify({
                'success': False,
                'error': 'Addresses array is required'
            }), 400
        
        addresses = data['addresses']
        if not isinstance(addresses, list):
            return jsonify({
                'success': False,
                'error': 'Addresses must be an array'
            }), 400
        
        if len(addresses) > 1000:  # Limit batch size
            return jsonify({
                'success': False,
                'error': 'Batch size too large (max 1000 addresses)'
            }), 400
        
        source_priority = data.get('source_priority', ['census', 'google'])
        batch_size = data.get('batch_size', 100)
        
        # Geocode addresses
        service = get_geocoding_service()
        results = service.batch_geocode(addresses, batch_size)
        
        # Calculate summary statistics
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'total': len(results),
                'successful': successful,
                'failed': failed,
                'success_rate': successful / len(results) * 100 if results else 0
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error batch geocoding: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@geocoding_bp.route('/reverse', methods=['POST'])
def reverse_geocode():
    """Reverse geocode coordinates to address (bonus feature)"""
    try:
        data = request.get_json()
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'success': False,
                'error': 'Latitude and longitude are required'
            }), 400
        
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        
        # For now, return a placeholder response
        # This would require implementing reverse geocoding
        return jsonify({
            'success': False,
            'error': 'Reverse geocoding not yet implemented'
        }), 501
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid latitude or longitude'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error reverse geocoding: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@geocoding_bp.route('/cache-stats', methods=['GET'])
def get_cache_stats():
    """Get cache performance metrics"""
    try:
        service = get_geocoding_service()
        stats = service.get_cache_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting cache stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@geocoding_bp.route('/usage', methods=['GET'])
def get_usage_stats():
    """Get API usage statistics"""
    try:
        service = get_geocoding_service()
        stats = service.get_usage_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting usage stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@geocoding_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        service = get_geocoding_service()
        
        # Test with a simple address
        test_result = service.geocode_address("123 Main St, Kansas City, MO")
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'test_geocoding': test_result['success']
        })
        
    except Exception as e:
        current_app.logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@geocoding_bp.route('/failed', methods=['GET'])
def get_failed_addresses():
    """Get addresses that failed to geocode"""
    try:
        limit = request.args.get('limit', 100, type=int)
        retry_threshold = request.args.get('retry_threshold', 3, type=int)
        
        service = get_geocoding_service()
        failed_addresses = service.get_failed_addresses(limit, retry_threshold)
        
        return jsonify({
            'success': True,
            'failed_addresses': failed_addresses,
            'count': len(failed_addresses)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting failed addresses: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@geocoding_bp.route('/failure-stats', methods=['GET'])
def get_failure_stats():
    """Get failure statistics"""
    try:
        service = get_geocoding_service()
        stats = service.get_failure_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting failure stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@geocoding_bp.route('/retry-failed', methods=['POST'])
def retry_failed_addresses():
    """Retry geocoding failed addresses"""
    try:
        data = request.get_json() or {}
        limit = data.get('limit', 50)
        
        service = get_geocoding_service()
        results = service.retry_failed_addresses(limit)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        current_app.logger.error(f"Error retrying failed addresses: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@geocoding_bp.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear geocoding cache (admin only)"""
    try:
        # In a real application, you'd want to check for admin permissions
        confirm = request.get_json().get('confirm', False) if request.get_json() else False
        
        if not confirm:
            return jsonify({
                'success': False,
                'error': 'Confirmation required'
            }), 400
        
        service = get_geocoding_service()
        service.clear_cache(confirm=True)
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error clearing cache: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Error handlers
@geocoding_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@geocoding_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

@geocoding_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
