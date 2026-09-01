# Error Handling & Validation

## Overview
PrimeTime must handle asset validation failures, runtime errors, and operator mistakes gracefully. Errors should never crash the application, and operators must receive clear feedback about issues.

## Asset Validation

### Video Validation

**Codec Requirements:**
- Video: H.264 (baseline, main, or high profile), maximum resolution 1920x1080
- Audio: AAC, MP3 (stereo or mono)
- Container: MP4
- Maximum file size: 500 MB

**Validation Process:**
1. Run `ffprobe` on file to extract metadata
2. Check codec strings match requirements
3. Check resolution ≤ 1920x1080
4. Check file size < 500 MB
5. Attempt to read first frame (verify file integrity)

**Error Codes:**
- `INVALID_CODEC` - Unsupported video/audio codec
- `RESOLUTION_TOO_HIGH` - Exceeds 1920x1080 (warning only, will scale)
- `FILE_TOO_LARGE` - Exceeds 500 MB
- `CORRUPT` - File unreadable or truncated
- `MISSING_AUDIO` - Video has no audio track (warning, not error)

**Fallback Behavior:**
- `RESOLUTION_TOO_HIGH`: Accept but log warning, Show View will scale down
- `MISSING_AUDIO`: Accept, operator warned
- All others: Reject asset, mark `error_state` in DB, operator notified

### Image Validation

**Requirements:**
- Formats: JPEG, PNG
- Maximum dimensions: 6000x6000 pixels
- Maximum file size: 50 MB per image
- Auto-scale to max 2200px on longest edge during preprocessing

**Validation Process:**
1. Use Pillow to open and validate format
2. Check dimensions
3. Check file size
4. Attempt EXIF extraction (for rotation)
5. Generate thumbnail (validates image integrity)

**Error Codes:**
- `INVALID_FORMAT` - Not JPEG or PNG
- `CORRUPT` - Image unreadable or truncated
- `FILE_TOO_LARGE` - Exceeds 50 MB
- `DIMENSIONS_TOO_LARGE` - Exceeds 6000x6000 (will auto-scale, but warn)

**Fallback Behavior:**
- All validation failures: Reject asset, mark `error_state`, operator notified

### Audio/Music Validation

**Requirements:**
- Formats: MP3, M4A (AAC)
- Bitrate: 128-320 kbps (warning for lower)
- Channels: Stereo or mono
- Maximum file size: 100 MB

**Validation Process:**
1. Use `mutagen` or `ffprobe` to extract metadata
2. Check format and codec
3. Check bitrate
4. Check file size

**Error Codes:**
- `INVALID_FORMAT` - Not MP3 or M4A
- `LOW_BITRATE` - Below 128 kbps (warning, not error)
- `FILE_TOO_LARGE` - Exceeds 100 MB
- `CORRUPT` - File unreadable

**Fallback Behavior:**
- `LOW_BITRATE`: Accept with warning badge in UI
- All others: Reject asset

## Runtime Errors

### Scene Load Failures

**Scenarios:**
1. Asset file missing (deleted after validation)
2. Video decode error during playback
3. Image texture load failure
4. WebGL context lost
5. Audio context suspended (browser policy)

**Error Handling:**
```javascript
try {
    await scene.load(asset);
} catch (error) {
    showView.sendError({
        code: 'SCENE_LOAD_FAILED',
        message: error.message,
        sceneId: currentScene.id,
        assetId: asset.id
    });
    // Auto-skip to next scene after 2 seconds
    setTimeout(() => {
        skipToNext();
    }, 2000);
}
```

**Error Codes:**
- `SCENE_LOAD_FAILED` - Generic load failure
- `ASSET_MISSING` - File not found on disk
- `VIDEO_DECODE_ERROR` - Video element decode failure
- `WEBGL_CONTEXT_LOST` - GPU context lost (rare, requires page reload)
- `AUDIO_SUSPENDED` - Browser blocked audio (requires user interaction)

**Fallback:**
- Show error text card: "Unable to load scene. Skipping..."
- Auto-skip to next scene after 2 seconds
- Operator sees warning badge in timeline

### WebSocket Disconnection

**Server Side:**
- Client disconnect detected, log event
- If Show View disconnected: Pause playback, save state
- If Operator UI disconnected: Continue playback, queue commands

**Client Side (Show View):**
- Display "Reconnecting..." overlay
- Stop rendering (or show frozen frame)
- Auto-reconnect with exponential backoff (1s, 2s, 4s, 8s, max 30s)
- On reconnect: Request state sync

**Client Side (Operator UI):**
- Show disconnected badge, disable controls
- Same auto-reconnect logic
- On reconnect: Request current timeline/state

**Error Codes:**
- `WEBSOCKET_DISCONNECTED` - Connection lost
- `WEBSOCKET_TIMEOUT` - Reconnect timeout exceeded (rare)

### Timeline Errors

**Invalid Timeline JSON:**
- Validation on save: Check required fields, valid scene types
- Error: `INVALID_TIMELINE_FORMAT` with field path
- Operator: Cannot save, error message shown

**Missing Assets:**
- On timeline load, check all referenced assets exist in DB
- Warning badges on timeline items with missing assets
- Error: `MISSING_ASSET` with asset path
- Fallback: Show placeholder scene (text card: "Asset missing: {path}")

**Circular References or Invalid Structure:**
- Validate timeline structure before saving
- Error: `INVALID_TIMELINE_STRUCTURE`
- Operator: Cannot save, validation errors listed

## Operator Feedback

### Toast Notifications

**Types:**
- `success` - Green, auto-dismiss 3s: "Timeline saved", "Asset imported"
- `warning` - Yellow, auto-dismiss 5s: "Low bitrate audio", "Resolution will be scaled"
- `error` - Red, manual dismiss: "Failed to load video", "Invalid codec"
- `info` - Blue, auto-dismiss 3s: "Photo added to slideshow", "Reconnected to server"

**Implementation:**
```javascript
function showToast(type, message, duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    if (duration) setTimeout(() => toast.remove(), duration);
}
```

### Warning Badges

**Timeline Items:**
- Yellow dot on item card = warning (low bitrate, scaled resolution)
- Red dot on item card = error (missing asset, invalid scene)
- Hover tooltip shows specific issue

**Asset Bins:**
- Red border around thumbnail = validation error
- Tooltip shows error message
- Asset cannot be added to timeline until fixed

### Error Logs Panel

**Operator UI Sidebar:**
- Expandable "Errors" panel showing recent errors
- Format: `[timestamp] [type] message`
- Clear button to dismiss resolved errors
- Click to jump to problematic timeline item/asset

## Graceful Degradation

### Scene Skip Strategy

1. **Detect error** (load failure, decode error, etc.)
2. **Show error scene** (text card: "Unable to load. Skipping...") for 2 seconds
3. **Auto-skip** to next valid scene
4. **Log error** to operator panel
5. **Continue playback** (don't stop entire show)

### Fallback Scenes

**For Missing Assets:**
```javascript
function createFallbackScene(assetPath) {
    return {
        sceneType: 'TextCards',
        params: {
            lines: [`Asset missing: ${assetPath}`],
            layout: 'center'
        },
        duration: 3000
    };
}
```

**For Decode Errors:**
- Show black screen for 1 second
- Skip to next scene
- Optionally play error sound (if audio context available)

### Performance Degradation

**FPS Drop Detection:**
- Monitor FPS in Show View (target 60 fps)
- If FPS < 55 for 2 seconds:
  - Reduce particle count in math visuals
  - Lower texture resolution for photos
  - Disable non-essential effects
- If FPS < 30 for 2 seconds:
  - Skip to simpler scene type
  - Disable all transitions
  - Show warning to operator

**Memory Pressure:**
- Monitor WebGL texture memory
- If approaching limit:
  - Drop preloaded scenes beyond "next"
  - Release old textures
  - Log warning to operator

## Logging

### Log Levels

- `DEBUG` - Development only, detailed state changes
- `INFO` - Normal operations: scene transitions, asset imports
- `WARNING` - Recoverable issues: low bitrate, scaled resolution
- `ERROR` - Failures: load errors, decode errors
- `CRITICAL` - System failures: DB corruption, WebGL context lost

### Log Format

```
[2025-01-15 14:23:45] [INFO] Asset imported: /assets/videos/intro.mp4 (id: abc123)
[2025-01-15 14:23:46] [WARNING] Low bitrate audio detected: 96 kbps
[2025-01-15 14:24:12] [ERROR] Scene load failed: ASSET_MISSING (asset_id: xyz789)
[2025-01-15 14:24:14] [INFO] Auto-skipped to next scene (index: 3)
```

### Log Rotation

- Rotate logs daily
- Keep last 7 days
- Max log file size: 10 MB
- Store in `logs/` directory

### Structured Logging

```python
import logging

logger = logging.getLogger('primetime')

logger.info('Asset imported', extra={
    'asset_id': asset_id,
    'asset_type': asset_type,
    'file_size': file_size
})

logger.error('Scene load failed', extra={
    'scene_id': scene_id,
    'error_code': error_code,
    'asset_id': asset_id
})
```

## Validation API

### Asset Validation Endpoint

```python
POST /api/assets/validate
{
    "path": "/assets/videos/test.mp4"
}

Response:
{
    "valid": true,
    "warnings": ["Resolution will be scaled to 1080p"],
    "metadata": { ... }
}

# or

{
    "valid": false,
    "error_code": "INVALID_CODEC",
    "error_message": "Video codec 'vp9' not supported. Use H.264.",
    "metadata": { ... }
}
```

### Timeline Validation

```python
POST /api/timeline/validate
{
    "timeline": { ... }
}

Response:
{
    "valid": true,
    "warnings": [
        {"item_index": 2, "message": "Asset missing: /assets/videos/old.mp4"}
    ]
}

# or

{
    "valid": false,
    "errors": [
        {"item_index": 0, "field": "sceneType", "message": "Unknown scene type 'BadScene'"}
    ]
}
```
