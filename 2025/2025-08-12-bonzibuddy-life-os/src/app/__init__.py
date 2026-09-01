from flask import Flask, render_template, redirect, url_for
from .core.config import load_config
from .core.db import init_db

def create_app():
    import os
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), "ui", "templates"),
                static_folder=os.path.join(os.path.dirname(__file__), "ui", "static"))
    load_config(app)
    init_db(app)

    # register blueprints
    from .domains.health.views import bp as health_bp
    from .domains.hobbies.views import bp as hobbies_bp
    from .domains.research.views import bp as research_bp
    from .domains.home.views import bp as home_bp

    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(hobbies_bp, url_prefix="/hobbies")
    app.register_blueprint(research_bp, url_prefix="/research")
    app.register_blueprint(home_bp, url_prefix="/home")

    @app.get("/")
    def _home():
        return render_template("home.html")

    @app.get("/privacy")
    def privacy():
        return render_template("privacy.html")

    @app.get("/terms")
    def terms():
        return render_template("terms.html")

    @app.get("/callback")
    def oura_callback():
        """Handle Oura OAuth callback"""
        from .domains.health.services import get_oura_user_info, store_oura_user
        from .domains.health.views import get_oura_oauth
        
        try:
            oauth = get_oura_oauth()
            token = oauth.oura.authorize_access_token()
            
            # Get user info from Oura
            user_info = get_oura_user_info(token['access_token'])
            
            # Store or update user and tokens
            user = store_oura_user(user_info, token)
            
            # Redirect to health dashboard with success message
            return redirect(url_for('health.index', oura_connected='true'))
        except Exception as e:
            app.logger.error(f"Oura callback error: {e}")
            return redirect(url_for('health.index', oura_error='true'))

    return app

# For `flask --app app run`
app = create_app()
