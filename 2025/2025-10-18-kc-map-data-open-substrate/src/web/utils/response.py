# Response Utilities

from flask import jsonify

def format_api_response(data, metadata=None, status_code=200):
    """Format consistent API response structure"""
    response = {
        'data': data,
        'metadata': metadata or {}
    }
    return jsonify(response), status_code

def format_error_response(error_message, status_code=500, details=None):
    """Format consistent error response structure"""
    response = {
        'error': error_message,
        'details': details
    }
    return jsonify(response), status_code
