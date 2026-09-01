# Testing Strategy

## Overview
PrimeTime uses pytest for backend testing, with unit tests for core logic, integration tests for API/WebSocket flows, and Playwright for end-to-end Operator UI workflows.

**Incremental Testing Approach:**
- Build tests alongside each phase
- Focus on what matters for current phase (don't test features not yet built)
- Performance tests for math visuals are critical early on
- Asset validation and timeline tests come later

**Testing Priority by Phase:**
1. **Phase 1B-1C**: Math visual rendering, FPS performance, parameter validation
2. **Phase 1D**: Audio playback, volume control
3. **Phase 1E**: Text rendering, animations
4. **Phase 1F**: Image loading, Ken Burns, slideshow
5. **Phase 1G**: Video validation, playback, sync
6. **Phase 1I**: Timeline editing, playback state machine, full integration

## Test Structure

```
tests/
  unit/
    test_asset_validator.py      # Asset validation logic
    test_timeline_parser.py       # Timeline JSON parsing/validation
    test_state_machine.py         # Playback state transitions
    test_database.py              # DB operations, queries
  integration/
    test_api_endpoints.py         # Flask REST API
    test_websocket_events.py      # SocketIO event flow
    test_asset_pipeline.py        # File watching, preprocessing
  e2e/
    test_operator_workflow.py     # Playwright: build timeline, playback
    test_show_view.py             # Playwright: scene rendering
  fixtures/
    sample_video.mp4              # Test video (H.264, 5 seconds)
    sample_photo.jpg              # Test photo (1920x1080)
    sample_audio.mp3              # Test audio (10 seconds)
    sample_timeline.json          # Valid timeline for testing
  conftest.py                     # Pytest fixtures (DB, Flask app, etc.)
```

## Unit Tests (pytest)

### Math Visual Parameter Validation Tests (Phase 1B-1C)

**File**: `tests/unit/test_math_visuals.py`

```python
import pytest
from primetime.scenes import validate_lissajous_params, validate_polar_roses_params

def test_validate_lissajous_params_valid():
    """Valid Lissajous parameters should pass"""
    params = {'a': 3, 'b': 2, 'delta': 1.57, 'speed': 1.0}
    result = validate_lissajous_params(params)
    assert result['valid'] is True

def test_validate_lissajous_params_out_of_range():
    """Speed out of range should fail"""
    params = {'a': 3, 'b': 2, 'delta': 1.57, 'speed': 10.0}
    result = validate_lissajous_params(params)
    assert result['valid'] is False
    assert 'speed' in result['errors']

def test_validate_lissajous_defaults():
    """Missing parameters should use defaults"""
    params = {'a': 3, 'b': 2}
    result = validate_lissajous_params(params)
    assert result['valid'] is True
    assert result['params']['delta'] == 1.57  # default
    assert result['params']['speed'] == 1.0   # default

def test_validate_polar_roses_k_integer():
    """K parameter should produce best results as integer"""
    params = {'k': 3.5}
    result = validate_polar_roses_params(params)
    assert result['valid'] is True
    assert 'k_non_integer' in result['warnings']  # Warning, not error
```

**Coverage Goals (Phase 1B-1C):**
- Parameter validation for each math preset
- Default value handling
- Range checking (speed, density, etc.)
- Warning vs error distinction

### Asset Validation Tests (Phase 1F-1G)

**File**: `tests/unit/test_asset_validator.py`

**Note**: Defer these tests until Phase 1F+ when asset pipeline is introduced.

```python
import pytest
from primetime.asset_validator import validate_video, validate_image, validate_audio

def test_validate_image_valid_jpeg():
    """Valid JPEG should pass"""
    result = validate_image('fixtures/sample_photo.jpg')
    assert result['valid'] is True

def test_validate_video_valid_h264():
    """Valid H.264 video should pass validation"""
    result = validate_video('fixtures/sample_video.mp4')
    assert result['valid'] is True
    assert result['error_code'] is None

def test_validate_video_invalid_codec():
    """VP9 video should fail validation"""
    result = validate_video('fixtures/invalid_vp9.mp4')
    assert result['valid'] is False
    assert result['error_code'] == 'INVALID_CODEC'
```

**Coverage Goals (Phase 1F-1G):**
- All validation error codes tested
- Edge cases: corrupted files, missing files, unsupported formats
- Warning vs error distinction

### Timeline Parser Tests (Phase 1I)

**File**: `tests/unit/test_timeline_parser.py`

**Note**: Defer timeline tests until Phase 1I when timeline editor is introduced.

```python
from primetime.timeline import parse_timeline, validate_timeline

def test_parse_valid_timeline():
    """Valid timeline JSON should parse correctly"""
    timeline_json = {
        "name": "Test",
        "theme": "neon-chalkboard",
        "items": [
            {"id": "m1", "sceneType": "MathVisuals", "params": {"preset": "lissajous"}}
        ]
    }
    timeline = parse_timeline(timeline_json)
    assert timeline.name == "Test"
    assert len(timeline.items) == 1

def test_validate_timeline_missing_required_field():
    """Timeline without 'items' should fail validation"""
    timeline_json = {"name": "Test"}
    result = validate_timeline(timeline_json)
    assert result['valid'] is False
    assert 'items' in result['errors'][0]['field']

def test_validate_timeline_invalid_scene_type():
    """Unknown sceneType should fail validation"""
    timeline_json = {
        "items": [{"sceneType": "BadScene", "params": {}}]
    }
    result = validate_timeline(timeline_json)
    assert result['valid'] is False
```

### State Machine Tests (Phase 1I)

**File**: `tests/unit/test_state_machine.py`

**Note**: Defer full state machine tests until Phase 1I. For Phase 1B-1C, test simple IDLE/RENDERING transitions only.

**Phase 1B-1C (Simplified State Machine):**
```python
from primetime.playback import SimpleStateMachine

def test_idle_to_rendering():
    """Starting scene should transition IDLE → RENDERING"""
    sm = SimpleStateMachine()
    assert sm.state == 'IDLE'
    sm.start_scene('Lissajous', {'a': 3, 'b': 2})
    assert sm.state == 'RENDERING'

def test_rendering_to_idle():
    """Stopping scene should transition RENDERING → IDLE"""
    sm = SimpleStateMachine()
    sm.state = 'RENDERING'
    sm.stop_scene()
    assert sm.state == 'IDLE'
```

**Phase 1I (Full State Machine):**
```python
from primetime.playback import PlaybackStateMachine

def test_idle_to_loading_transition():
    """Loading timeline should transition IDLE → LOADING"""
    sm = PlaybackStateMachine()
    assert sm.state == 'IDLE'
    sm.load_timeline(mock_timeline)
    assert sm.state == 'LOADING'

def test_loading_to_playing_transition():
    """Assets ready + play should transition LOADING → PLAYING"""
    sm = PlaybackStateMachine()
    sm.load_timeline(mock_timeline)
    sm.assets_ready()
    sm.play()
    assert sm.state == 'PLAYING'
```

### Database Tests

**File**: `tests/unit/test_database.py`

```python
import pytest
from primetime import create_app, db
from primetime.models import Asset, Timeline, Setting

@pytest.fixture
def app():
    """Create test Flask app with in-memory SQLite DB"""
    app = create_app(testing=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_insert_asset(app):
    """Insert asset should create row"""
    with app.app_context():
        asset = Asset(
            id='test123',
            type='video',
            path='/test.mp4',
            file_size_bytes=1000,
            added_at=1234567890
        )
        db.session.add(asset)
        db.session.commit()
        
        result = Asset.query.get('test123')
        assert result.id == 'test123'
        assert result.type == 'video'

def test_query_assets_by_type(app):
    """Query assets by type should filter correctly"""
    with app.app_context():
        db.session.add(Asset(id='v1', type='video', path='/v1.mp4', file_size_bytes=1000, added_at=1234567890))
        db.session.add(Asset(id='p1', type='photo', path='/p1.jpg', file_size_bytes=500, added_at=1234567890))
        db.session.commit()
        
        videos = Asset.query.filter_by(type='video').all()
        assert len(videos) == 1
        assert videos[0].type == 'video'

def test_timeline_save_and_load(app):
    """Save timeline should persist, load should retrieve"""
    with app.app_context():
        timeline_json = '{"name": "Test", "items": []}'
        timeline = Timeline(
            name='Test',
            timeline_json=timeline_json,
            created_at=1234567890,
            updated_at=1234567890
        )
        db.session.add(timeline)
        db.session.commit()
        
        loaded = Timeline.query.filter_by(name='Test').first()
        assert loaded.name == "Test"
        assert json.loads(loaded.timeline_json)['name'] == "Test"
```

## Integration Tests

### API Endpoint Tests

**File**: `tests/integration/test_api_endpoints.py`

```python
import pytest
from primetime import create_app

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

def test_asset_validate_endpoint(client):
    """POST /api/assets/validate should return validation result"""
    response = client.post('/api/assets/validate', json={
        'path': 'fixtures/sample_video.mp4'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'valid' in data

def test_timeline_save_endpoint(client):
    """POST /api/timeline/save should save timeline"""
    response = client.post('/api/timeline/save', json={
        'timeline': {'name': 'Test', 'items': []}
    })
    assert response.status_code == 200
    assert response.get_json()['success'] is True

def test_asset_list_endpoint(client):
    """GET /api/assets?type=video should return video assets"""
    response = client.get('/api/assets?type=video')
    assert response.status_code == 200
    data = response.get_json()
    assert all(a['type'] == 'video' for a in data['assets'])
```

### WebSocket Event Tests

**File**: `tests/integration/test_websocket_events.py`

```python
import pytest
from flask_socketio import SocketIOTestClient
from primetime import create_app, socketio

@pytest.fixture
def socket_client():
    app = create_app(testing=True)
    client = socketio.test_client(app, namespace='/show')
    yield client
    client.disconnect()

def test_show_load_timeline_event(socket_client):
    """SHOW_LOAD_TIMELINE should load timeline in show view"""
    timeline = {'name': 'Test', 'items': []}
    socket_client.emit('SHOW_LOAD_TIMELINE', {'timeline': timeline})
    # Check that server received and processed
    received = socket_client.get_received('/show')
    # Assert appropriate response

def test_show_play_event(socket_client):
    """SHOW_PLAY should start playback"""
    socket_client.emit('SHOW_PLAY', {})
    # Assert state changed to PLAYING

def test_show_status_telemetry(socket_client):
    """Show View should send SHOW_STATUS periodically"""
    # Mock show view sending status
    socket_client.emit('SHOW_STATUS', {
        'fps': 60,
        'sceneId': 'v1',
        'itemIndex': 0,
        'timecodeMs': 5000
    })
    # Assert server received and stored telemetry
```

### Asset Pipeline Tests

**File**: `tests/integration/test_asset_pipeline.py`

```python
import tempfile
import shutil
from primetime.asset_pipeline import AssetWatcher

def test_file_watcher_detects_new_photo():
    """File watcher should detect new photo and index it"""
    with tempfile.TemporaryDirectory() as tmpdir:
        watcher = AssetWatcher(tmpdir)
        # Copy test photo
        shutil.copy('fixtures/sample_photo.jpg', tmpdir / 'new_photo.jpg')
        # Wait for watch event
        watcher.process_queue()
        # Assert asset added to DB

def test_photo_preprocessing_scales_large_image():
    """Preprocessing should scale large image to 2200px"""
    result = preprocess_image('fixtures/large_photo.jpg')
    assert result['width'] <= 2200 or result['height'] <= 2200

def test_video_thumbnail_extraction():
    """Video preprocessing should extract first frame thumbnail"""
    result = preprocess_video('fixtures/sample_video.mp4')
    assert 'thumbnail_path' in result
    assert os.path.exists(result['thumbnail_path'])
```

## End-to-End Tests (Playwright)

### Setup

```bash
pip install playwright pytest-playwright
playwright install chromium
```

**File**: `tests/e2e/test_operator_workflow.py`

```python
import pytest
from playwright.sync_api import Page, expect

@pytest.fixture
def operator_page(page: Page, flask_server):
    """Navigate to operator UI"""
    page.goto('http://localhost:5000/operator')
    yield page

def test_build_timeline(operator_page: Page):
    """Operator can build timeline from UI"""
    # Drag video from asset bin to timeline
    video_thumb = operator_page.locator('[data-asset-type="video"]').first
    timeline = operator_page.locator('.timeline-track')
    video_thumb.drag_to(timeline)
    
    # Assert timeline item appears
    timeline_item = operator_page.locator('.timeline-item')
    expect(timeline_item).to_be_visible()
    
    # Save timeline
    operator_page.click('button:has-text("Save")')
    expect(operator_page.locator('.toast-success')).to_be_visible()

def test_playback_controls(operator_page: Page):
    """Transport controls work correctly"""
    # Load timeline
    operator_page.click('button:has-text("Load Timeline")')
    
    # Click play
    operator_page.click('button[aria-label="Play"]')
    
    # Assert status shows playing
    status = operator_page.locator('.status-bar')
    expect(status).to_contain_text('Playing')
    
    # Click pause
    operator_page.click('button[aria-label="Pause"]')
    expect(status).to_contain_text('Paused')

def test_hotkeys(operator_page: Page):
    """Hotkeys trigger actions"""
    operator_page.press('body', 'Space')  # Play/Pause
    # Assert playback state changed
    
    operator_page.press('body', 'ArrowRight')  # Next
    # Assert timeline advanced

def test_countdown_cue(operator_page: Page):
    """Countdown cue button triggers countdown"""
    operator_page.click('button:has-text("Countdown")')
    # Assert countdown starts on show view (need to check show view page)
```

**File**: `tests/e2e/test_show_view.py`

```python
def test_show_view_loads_timeline(show_page: Page):
    """Show View loads and displays timeline"""
    # Timeline should be sent via WebSocket
    # Assert canvas is visible and rendering
    canvas = show_page.locator('#show-canvas')
    expect(canvas).to_be_visible()

def test_video_scene_plays(show_page: Page):
    """Video scene plays correctly"""
    # Load timeline with video
    # Assert video element plays
    video = show_page.locator('#show-video')
    expect(video).to_have_property('paused', False)

def test_scene_transition(show_page: Page):
    """Scene transitions work smoothly"""
    # Load timeline with multiple scenes
    # Wait for transition
    # Assert next scene is visible
```

## Performance Tests (Critical for Phase 1B-1C)

### FPS Benchmark Tests

**File**: `tests/performance/test_fps.py`

**Priority**: HIGH - These tests are critical from Phase 1B onwards.

```python
import time
import pytest

def test_lissajous_sustains_60fps():
    """Lissajous preset should maintain 60 fps (Phase 1B acceptance criteria)"""
    scene = create_math_scene('lissajous', {'a': 3, 'b': 2, 'delta': 1.57})
    fps_samples = []
    
    for _ in range(300):  # 5 seconds at 60fps
        start = time.time()
        scene.render()
        frame_time = (time.time() - start) * 1000
        fps = 1000 / frame_time if frame_time > 0 else 60
        fps_samples.append(fps)
    
    avg_fps = sum(fps_samples) / len(fps_samples)
    assert avg_fps >= 55, f"Average FPS {avg_fps} below threshold"
    assert min(fps_samples) >= 50, f"Min FPS {min(fps_samples)} too low"

def test_polar_roses_sustains_60fps():
    """Polar Roses preset should maintain 60 fps (Phase 1C)"""
    scene = create_math_scene('polar_roses', {'k': 3})
    fps_samples = measure_fps(scene, duration_seconds=5)
    assert average(fps_samples) >= 55

def test_all_math_presets_performance():
    """All math presets should meet performance requirements (Phase 1C)"""
    presets = ['lissajous', 'polar_roses', 'spirograph', 'digits_rain', 'ulam_spiral']
    
    for preset_name in presets:
        scene = create_math_scene(preset_name)
        fps_samples = measure_fps(scene, duration_seconds=3)
        avg_fps = average(fps_samples)
        assert avg_fps >= 55, f"{preset_name} failed: {avg_fps} fps"

def test_scene_switching_latency():
    """Switching between presets should be fast (Phase 1C)"""
    scene1 = create_math_scene('lissajous')
    scene1.cleanup()
    
    start = time.time()
    scene2 = create_math_scene('polar_roses')
    scene2.init()
    latency = (time.time() - start) * 1000
    
    assert latency < 500, f"Scene switch took {latency}ms, expected < 500ms"
```

**Helper Functions:**
```python
def measure_fps(scene, duration_seconds=5):
    """Measure FPS for a scene over given duration"""
    fps_samples = []
    frames = int(duration_seconds * 60)
    
    for _ in range(frames):
        start = time.time()
        scene.render()
        frame_time = (time.time() - start) * 1000
        fps = 1000 / frame_time if frame_time > 0 else 60
        fps_samples.append(fps)
    
    return fps_samples

def average(samples):
    return sum(samples) / len(samples) if samples else 0
```

## Test Data

### Required Test Assets

**Location**: `tests/fixtures/`

1. **sample_video.mp4** (5-10 seconds)
   - H.264 baseline profile, AAC audio
   - 1920x1080 resolution
   - < 10 MB

2. **sample_photo.jpg** (1920x1080)
   - Standard JPEG, EXIF data present
   - < 2 MB

3. **invalid_video.webm** (for negative tests)
   - VP9 codec (should fail validation)

4. **sample_audio.mp3** (10 seconds)
   - 128 kbps MP3
   - < 1 MB

5. **sample_timeline.json**
   - Valid timeline with 3-4 items
   - Mix of scene types

## Running Tests

### All Tests
```bash
pytest
```

### Specific Suite
```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### With Coverage
```bash
pytest --cov=primetime --cov-report=html
```

### Watch Mode (auto-rerun on changes)
```bash
pytest-watch
```

## Test Coverage Goals (By Phase)

### Phase 1B-1C (Math Visuals)
- **Unit tests**: Parameter validation for each preset
- **Performance tests**: FPS benchmarks for all presets (60+ fps target)
- **Integration tests**: WebSocket events (start/stop scene, update params)
- **Manual tests**: Visual quality, smooth rendering

### Phase 1D (Music)
- **Unit tests**: Audio buffer loading, volume control
- **Integration tests**: Music playback WebSocket events
- **Manual tests**: No audio/rendering interference

### Phase 1E-1F (Text, Photos)
- **Unit tests**: Text layout, image loading
- **Integration tests**: Scene rendering, animations
- **Manual tests**: Visual quality, transitions

### Phase 1G (Video)
- **Unit tests**: Video validation (codec checks)
- **Integration tests**: Video playback, sync
- **Manual tests**: No audio/video desync

### Phase 1I (Timeline & Integration)
- **Unit tests**: 80%+ coverage of core logic (validation, parsing, state machine)
- **Integration tests**: All API endpoints and WebSocket events
- **E2E tests**: Critical operator workflows (build timeline, playback, cues)
- **Performance tests**: Sustained 60fps for full 20-minute timeline

## Continuous Integration

**GitHub Actions** (or similar):
- Run unit + integration tests on every commit
- Run E2E tests on pull requests
- Run performance benchmarks nightly
- Fail PR if coverage drops below 80%
