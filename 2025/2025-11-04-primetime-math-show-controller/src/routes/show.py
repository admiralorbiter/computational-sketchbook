"""Show View route handler."""
from flask import Blueprint, send_from_directory

bp = Blueprint('show', __name__)


@bp.route('/show')
def show_view():
    """Serve the Show View page."""
    return send_from_directory('static/show', 'index.html')

