"""Flask application entry point for PrimeTime."""
import os
from flask import Flask
from flask_socketio import SocketIO
from flask_migrate import Migrate
from config import config
from models import db
from database import init_db
from routes import register_blueprints

# Create Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

# Initialize extensions
db.init_app(app)
socketio = SocketIO(
    app, 
    async_mode=app.config['SOCKETIO_ASYNC_MODE'],
    cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS']
)
migrate = Migrate(app, db)

# Register blueprints
register_blueprints(app)

# Database initialization will be handled in __main__ block


# SocketIO event handlers
@socketio.on('connect', namespace='/control')
def handle_control_connect(auth):
    """Handle operator UI connection."""
    print(f'Operator UI connected: {auth}')
    return {'status': 'connected'}


@socketio.on('connect', namespace='/show')
def handle_show_connect(auth):
    """Handle show view connection."""
    print(f'Show View connected: {auth}')
    return {'status': 'connected'}


@socketio.on('disconnect', namespace='/control')
def handle_control_disconnect():
    """Handle operator UI disconnection."""
    print('Operator UI disconnected')


@socketio.on('disconnect', namespace='/show')
def handle_show_disconnect():
    """Handle show view disconnection."""
    print('Show View disconnected')


# Ping/Pong handlers for connection testing
@socketio.on('CONTROL_PING', namespace='/control')
def handle_control_ping(data):
    """Handle ping from operator UI and relay to show view."""
    print(f'Received ping from operator UI: {data}')
    # Relay ping to show view
    socketio.emit('SHOW_PING', data, namespace='/show')


@socketio.on('SHOW_PONG', namespace='/show')
def handle_show_pong(data):
    """Handle pong from show view and relay back to operator UI."""
    print(f'Received pong from show view: {data}')
    # Relay pong back to operator UI
    socketio.emit('CONTROL_PONG', data, namespace='/control')


# Scene control handlers (Phase 1B)
@socketio.on('CONTROL_START_SCENE', namespace='/control')
def handle_control_start_scene(data):
    """Handle start scene command from operator UI."""
    print(f'Start scene command: {data}')
    # Relay to show view
    socketio.emit('SHOW_START_SCENE', data, namespace='/show')


@socketio.on('CONTROL_UPDATE_PARAMS', namespace='/control')
def handle_control_update_params(data):
    """Handle parameter update from operator UI."""
    print(f'Update params command: {data}')
    # Relay to show view
    socketio.emit('SHOW_UPDATE_PARAMS', data, namespace='/show')


@socketio.on('CONTROL_STOP_SCENE', namespace='/control')
def handle_control_stop_scene(data):
    """Handle stop scene command from operator UI."""
    print('Stop scene command')
    # Relay to show view
    socketio.emit('SHOW_STOP_SCENE', {}, namespace='/show')


@socketio.on('SHOW_FPS_UPDATE', namespace='/show')
def handle_show_fps_update(data):
    """Handle FPS update from show view and relay to operator UI."""
    # Relay FPS to operator UI
    socketio.emit('SHOW_FPS_UPDATE', data, namespace='/control')


@app.route('/')
def index():
    """Root route redirects to operator UI."""
    from flask import redirect
    return redirect('/operator')


@app.route('/themes/<path:filename>')
def serve_theme(filename):
    """Serve theme JSON files."""
    from flask import send_from_directory
    import os
    themes_dir = os.path.join(app.root_path, 'themes')
    return send_from_directory(themes_dir, filename)


if __name__ == '__main__':
    # Ensure data directory exists
    data_dir = app.config['DATA_DIR']
    if isinstance(data_dir, str):
        os.makedirs(data_dir, exist_ok=True)
    else:
        data_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # Run application
    socketio.run(app, debug=app.config['DEBUG'], host='0.0.0.0', port=5000)

