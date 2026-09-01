"""SQLAlchemy models for PrimeTime application."""
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()


class Timeline(db.Model):
    """Timeline configuration model."""
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


class Asset(db.Model):
    """Media asset metadata model."""
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


class AssetThumbnail(db.Model):
    """Cached thumbnail images model."""
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


class Setting(db.Model):
    """Application settings key-value store."""
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


class PlaybackState(db.Model):
    """Current playback position and state."""
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

