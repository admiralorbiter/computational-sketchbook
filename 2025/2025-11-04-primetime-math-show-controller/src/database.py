"""Database initialization and utility functions."""
import json
import time
from models import db, Setting, PlaybackState


def init_db():
    """Initialize database tables and seed default data."""
    # Create all tables
    db.create_all()
    
    # Seed default settings if they don't exist
    seed_default_settings()
    
    # Initialize playback state
    init_playback_state()


def seed_default_settings():
    """Seed default application settings."""
    default_settings = [
        {
            'key': 'theme',
            'value': json.dumps({
                'id': 'neon-chalkboard',
                'name': 'Neon Chalkboard',
                'bg_color': '#0f1115',
                'fg_color': '#F4F4F4',
                'accent_green': '#39FF14',
                'accent_cyan': '#00E5FF'
            })
        },
        {
            'key': 'master_volume',
            'value': '0.8'
        },
        {
            'key': 'operator_ui_layout',
            'value': json.dumps({
                'left_panel_width': 250,
                'right_panel_width': 300,
                'timeline_height': 200
            })
        }
    ]
    
    current_time = int(time.time())
    for setting_data in default_settings:
        existing = Setting.query.filter_by(key=setting_data['key']).first()
        if not existing:
            setting = Setting(
                key=setting_data['key'],
                value=setting_data['value'],
                updated_at=current_time
            )
            db.session.add(setting)
    
    db.session.commit()


def init_playback_state():
    """Initialize playback state singleton row."""
    existing = PlaybackState.query.filter_by(id=1).first()
    if not existing:
        playback_state = PlaybackState(
            id=1,
            updated_at=int(time.time())
        )
        db.session.add(playback_state)
        db.session.commit()

