# Setup, Runbook & Deployment

## Environment
- Python 3.10+
- Chrome/Chromium 90+ for Show View (recommended for best WebGL/WebAudio performance)
- Modern browser for Operator UI (Chrome, Firefox, Edge, Safari)

## Runbook
1. Place media in `/assets/...`.
2. Launch server (`flask run` or packaged script).
3. Open two windows:
   - **Projector**: `/show` in fullscreen/kiosk.
   - **Operator**: `/operator` on laptop display.
4. Load or build `timeline.json` from Operator UI.
5. Sound check: set master volume; verify no clipping.
6. Go live.

## Developer Setup

### Initial Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database migrations (first time only)
flask db init

# Create initial migration (if models exist)
flask db migrate -m "Initial migration"

# Apply migrations to create database
flask db upgrade

# Create asset folders
mkdir -p assets/photos assets/videos assets/music assets/logos
```

### Running Development Server
```bash
# Set Flask environment variables (optional)
export FLASK_APP=app.py
export FLASK_ENV=development

# Run Flask with auto-reload
flask run
# Or: python app.py

# Server runs on http://localhost:5000
```

### Development Workflow
1. **Start Flask**: `flask run` (debug mode auto-reloads on Python file changes)
2. **Open Show View**: Navigate to `http://localhost:5000/show`, press F11 for fullscreen
3. **Open Operator UI**: Navigate to `http://localhost:5000/operator` in separate window/tab
4. **Edit Code**: 
   - Python files: Flask auto-reloads server on save
   - JavaScript/HTML: Refresh browser manually (Cmd/Ctrl+R)
5. **Debug**: Use browser DevTools (F12) for JavaScript debugging, Network tab for WebSocket inspection

### Optional: Hot Reload for Frontend
- Browser extension: "Live Server" or "Auto Refresh Plus"
- Or use browser DevTools with "Disable cache" enabled

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=primetime --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
```

## Packaging
- **Production Build**: 
  - Python: `pip install -r requirements.txt`
  - Optional: Use `esbuild` for JavaScript minification (production only)
  - Optional: PyInstaller/Briefcase to ship a single app bundle
- **No Node.js required** - Vanilla JS works directly in browser

## Fallbacks
- Export a safe MP4 of the timeline (without live photos) for venues that require files.
- Keep a static sponsor slide on a USB stick.
