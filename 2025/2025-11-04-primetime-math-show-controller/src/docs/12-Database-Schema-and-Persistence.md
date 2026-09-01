# Database Schema & Persistence

## Overview
PrimeTime uses SQLite with Flask-SQLAlchemy ORM for persistence. The database stores timelines, asset metadata, settings, thumbnails, and playback state. SQLAlchemy provides type safety, relationship management, and migration support.

## Models

### `Timeline`
Stores timeline configurations (serialized JSON) with metadata.

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Timeline(db.Model):
    __tablename__ = 'timelines'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    timeline_json = db.Column(db.Text, nullable=False)  # JSON string of full timeline
    theme_id = db.Column(db.String(50), default='neon-chalkboard')
    created_at = db.Column(db.Integer, nullable=False)  # Unix timestamp
    updated_at = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=False)  # Only one active at a time
    notes = db.Column(db.Text)
    
    __table_args__ = (
        db.Index('idx_timelines_active', 'is_active'),
        db.Index('idx_timelines_updated', 'updated_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'timeline_json': self.timeline_json,
            'theme_id': self.theme_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'notes': self.notes
        }
```

**timeline_json** structure matches `03-Timeline-and-Data-Contracts.md`:
- `name`, `theme`, `items[]` array

### `Asset`
File metadata for all media assets (photos, videos, music, logos).

```python
class Asset(db.Model):
    __tablename__ = 'assets'
    
    id = db.Column(db.String(255), primary_key=True)  # UUID or hash-based ID
    type = db.Column(db.String(20), nullable=False)  # 'photo' | 'video' | 'music' | 'logo'
    path = db.Column(db.String(500), nullable=False, unique=True)  # Relative path from /assets
    width = db.Column(db.Integer, nullable=True)  # NULL for audio
    height = db.Column(db.Integer, nullable=True)  # NULL for audio
    duration_ms = db.Column(db.Integer, nullable=True)  # NULL for photos/logos
    file_size_bytes = db.Column(db.BigInteger, nullable=False)
    hash = db.Column(db.String(64))  # Content hash (SHA256 or perceptual hash)
    mime_type = db.Column(db.String(100))  # 'video/mp4', 'image/jpeg', etc.
    codec_info = db.Column(db.Text)  # JSON: {"video": "h264", "audio": "aac"} or null
    added_at = db.Column(db.Integer, nullable=False)  # Unix timestamp
    validated_at = db.Column(db.Integer, nullable=True)  # NULL if validation pending/failed
    error_state = db.Column(db.String(50), nullable=True)  # NULL if OK, else error code
    metadata_json = db.Column(db.Text)  # Additional JSON: EXIF, tags, etc.
    
    # Relationship to thumbnails
    thumbnails = db.relationship('AssetThumbnail', backref='asset', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_assets_type', 'type'),
        db.Index('idx_assets_path', 'path'),
        db.Index('idx_assets_added', 'added_at'),
        db.Index('idx_assets_validated', 'validated_at', 'error_state'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'path': self.path,
            'width': self.width,
            'height': self.height,
            'duration_ms': self.duration_ms,
            'file_size_bytes': self.file_size_bytes,
            'hash': self.hash,
            'mime_type': self.mime_type,
            'codec_info': self.codec_info,
            'added_at': self.added_at,
            'validated_at': self.validated_at,
            'error_state': self.error_state,
            'metadata_json': self.metadata_json
        }
```

**error_state** values:
- `None` = valid
- `'INVALID_CODEC'` = unsupported codec
- `'FILE_MISSING'` = file deleted/moved
- `'CORRUPT'` = file unreadable
- `'TOO_LARGE'` = exceeds size limits

### `AssetThumbnail`
Cached thumbnail images (JPEG blobs) for fast UI display.

```python
class AssetThumbnail(db.Model):
    __tablename__ = 'asset_thumbnails'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.String(255), db.ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    size = db.Column(db.String(20), nullable=False)  # 'small' (150px) | 'medium' (300px) | 'large' (600px)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    thumbnail_blob = db.Column(db.LargeBinary, nullable=False)  # JPEG bytes
    created_at = db.Column(db.Integer, nullable=False)  # Unix timestamp
    
    __table_args__ = (
        db.UniqueConstraint('asset_id', 'size', name='uq_asset_thumbnail'),
        db.Index('idx_thumbnails_asset', 'asset_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'size': self.size,
            'width': self.width,
            'height': self.height,
            'created_at': self.created_at
            # Note: thumbnail_blob not included in dict (too large, access via attribute)
        }
```

**Blob sizes** (approximate):
- small: ~5-15 KB
- medium: ~15-40 KB
- large: ~40-100 KB

### `Setting`
Key-value store for application settings, theme preferences, and operator UI state.

```python
class Setting(db.Model):
    __tablename__ = 'settings'
    
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text, nullable=False)  # JSON string or plain text
    updated_at = db.Column(db.Integer, nullable=False)  # Unix timestamp
    
    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at
        }
```

**Common keys:**
- `theme` - Current theme JSON
- `master_volume` - Float 0.0-1.0
- `operator_ui_layout` - UI panel dimensions/visibility
- `last_timeline_id` - Most recently loaded timeline

**Default rows** inserted on first run:
```python
default_settings = [
    Setting(key='theme', value='{"id": "neon-chalkboard", ...}', updated_at=int(time.time())),
    Setting(key='master_volume', value='0.8', updated_at=int(time.time())),
    Setting(key='operator_ui_layout', value='{"left_panel_width": 250, ...}', updated_at=int(time.time()))
]
```

### `PlaybackState`
Current playback position and state (for recovery after disconnect).

```python
class PlaybackState(db.Model):
    __tablename__ = 'playback_state'
    
    id = db.Column(db.Integer, primary_key=True)  # Always 1
    timeline_id = db.Column(db.Integer, db.ForeignKey('timelines.id'), nullable=True)
    current_index = db.Column(db.Integer, nullable=False, default=0)  # Index into timeline.items[]
    timecode_ms = db.Column(db.Integer, nullable=False, default=0)  # Position within current item
    is_playing = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.Integer, nullable=False)  # Unix timestamp
    
    __table_args__ = (
        db.CheckConstraint('id = 1', name='check_single_row'),
    )
    
    def to_dict(self):
        return {
            'timeline_id': self.timeline_id,
            'current_index': self.current_index,
            'timecode_ms': self.timecode_ms,
            'is_playing': self.is_playing,
            'updated_at': self.updated_at
        }
```

**Initialization**: Insert single row on app init if it doesn't exist:
```python
if not PlaybackState.query.filter_by(id=1).first():
    db.session.add(PlaybackState(id=1, updated_at=int(time.time())))
    db.session.commit()
```

**Recovery logic**: On Show View reconnect, server sends `SHOW_LOAD_TIMELINE` + `SHOW_JUMP` to resume from this state.

## Database Initialization

### Flask-SQLAlchemy Setup

```python
# app.py or __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/primetime.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models to register them
from models import Timeline, Asset, AssetThumbnail, Setting, PlaybackState

# Create tables on first run
@app.before_first_request
def init_db():
    db.create_all()
    # Seed default settings
    if not Setting.query.filter_by(key='theme').first():
        seed_default_settings()
    # Initialize playback state
    if not PlaybackState.query.filter_by(id=1).first():
        db.session.add(PlaybackState(id=1, updated_at=int(time.time())))
        db.session.commit()
```

## Migration Strategy

### Flask-Migrate (Alembic)

Use Flask-Migrate for database schema migrations:

```bash
# Initialize migrations (first time)
flask db init

# Create migration after model changes
flask db migrate -m "Add new column to assets table"

# Apply migration
flask db upgrade

# Rollback if needed
flask db downgrade
```

**Benefits:**
- Version-controlled schema changes
- Automatic migration script generation
- Easy rollback capability
- Works with team development

### Backup & Restore
- **Backup**: Copy `.db` file before major timeline edits or updates
- **Restore**: Replace `.db` file, restart server, run `flask db upgrade` if schema changed
- **Export**: Timeline JSON can be exported/imported independently of DB

## Performance Considerations

1. **Thumbnails**: Generate on asset add, store in DB (faster than filesystem for small blobs)
2. **Indexes**: All foreign keys and common query paths indexed
3. **VACUUM**: Periodic `VACUUM` recommended after bulk deletes
4. **WAL mode**: Enable Write-Ahead Logging for better concurrent reads
   ```sql
   PRAGMA journal_mode=WAL;
   ```

## Data Access Patterns

### Timeline Loading
```python
# Get active timeline
active_timeline = Timeline.query.filter_by(is_active=True).first()
if active_timeline:
    timeline_data = json.loads(active_timeline.timeline_json)
```

### Asset Listing (by type)
```python
# Get assets with thumbnails
from sqlalchemy.orm import joinedload

assets = Asset.query.options(
    joinedload(Asset.thumbnails)
).filter(
    Asset.type == 'video',
    Asset.error_state.is_(None)
).order_by(
    Asset.added_at.desc()
).all()

# Access thumbnail for each asset
for asset in assets:
    medium_thumb = next((t for t in asset.thumbnails if t.size == 'medium'), None)
    if medium_thumb:
        thumbnail_blob = medium_thumb.thumbnail_blob
```

### Recent Assets (for slideshow)
```python
# Get recent photos for slideshow
recent_photos = Asset.query.filter(
    Asset.type == 'photo',
    Asset.error_state.is_(None)
).order_by(
    Asset.added_at.desc()
).limit(100).all()
```

### Example CRUD Operations

```python
# Create asset
new_asset = Asset(
    id=generate_uuid(),
    type='video',
    path='/assets/videos/intro.mp4',
    file_size_bytes=1024000,
    added_at=int(time.time())
)
db.session.add(new_asset)
db.session.commit()

# Update asset
asset = Asset.query.get(asset_id)
asset.validated_at = int(time.time())
asset.error_state = None
db.session.commit()

# Delete asset (cascades to thumbnails)
asset = Asset.query.get(asset_id)
db.session.delete(asset)
db.session.commit()

# Query with filters
valid_videos = Asset.query.filter(
    Asset.type == 'video',
    Asset.error_state.is_(None),
    Asset.width <= 1920,
    Asset.height <= 1080
).all()
```
