"""Route blueprint registration."""
from . import api, operator, show

def register_blueprints(app):
    """Register all route blueprints with the Flask app."""
    app.register_blueprint(api.bp)
    app.register_blueprint(operator.bp)
    app.register_blueprint(show.bp)

