"""Operator UI route handler."""
from flask import Blueprint, send_from_directory
from config import Config

bp = Blueprint('operator', __name__)


@bp.route('/operator')
def operator_ui():
    """Serve the Operator UI page."""
    return send_from_directory('static/operator', 'index.html')

