"""REST API endpoints."""
from flask import Blueprint, jsonify
from models import db

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'PrimeTime API is running'
    })


@bp.route('/status', methods=['GET'])
def status():
    """Application status endpoint."""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'ok',
        'database': db_status
    })

