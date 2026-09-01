from __future__ import annotations
import os
from datetime import datetime, timezone
from flask import Flask, jsonify
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__, 
                template_folder="../templates",
                static_folder="../static")

    # Config
    app.config.setdefault("DATA_DIR", os.path.abspath(os.getenv("DATA_DIR", "data")))
    app.config.setdefault("CACHE_DIR", os.path.join(app.config["DATA_DIR"], "_cache"))
    os.makedirs(app.config["CACHE_DIR"], exist_ok=True)

    # Blueprints
    from .blueprints.api import api_bp
    from .blueprints.pages import pages_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(pages_bp)

    @app.get("/api/health")
    def api_health():
        return jsonify({"ok": True, "ts": datetime.now(timezone.utc).isoformat()}), 200

    return app
