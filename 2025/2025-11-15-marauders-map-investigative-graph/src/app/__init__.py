from flask import Flask
from flask_cors import CORS
from pathlib import Path

from .config import get_config
from .db import init_db
from .routes import register_routes


def create_app() -> Flask:
    # Serve static files (index.html, app.js) from client/static at /static
    app = Flask(
        __name__,
        static_folder="client/static",
        static_url_path="/static",
    )

    config = get_config()
    app.config.update(config)

    # Ensure workspace-related folders exist
    data_dir = Path(app.config["DATA_DIR"])
    data_dir.mkdir(parents=True, exist_ok=True)

    CORS(app)

    init_db(app)
    register_routes(app)

    @app.get("/")
    def index():
        # Use Flask's configured static folder for the shell
        return app.send_static_file("index.html")

    return app


