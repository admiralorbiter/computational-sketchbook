"""Generate standalone playable index.html from widget template."""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from kc_paths.widget import render_playable_game

widget_html = render_playable_game(height=840).data

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Kansas City — Paths Not Taken (Mission 01)</title>
  <style>
    body {{
      margin: 0;
      padding: 24px;
      background: #020617;
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      min-height: 100vh;
    }}
    .header-bar {{
      max-width: 1280px;
      width: 100%;
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .header-bar h1 {{
      font-size: 1.35rem;
      color: #38bdf8;
      margin: 0;
    }}
    .header-bar p {{
      font-size: 0.85rem;
      color: #94a3b8;
      margin: 4px 0 0 0;
    }}
    .game-wrapper {{
      max-width: 1280px;
      width: 100%;
      height: 840px;
    }}
  </style>
</head>
<body>
  <div class="header-bar">
    <div>
      <h1>Kansas City — Paths Not Taken</h1>
      <p>Mission 01: A Future in Healthcare · Ruskin High School (Hickman Mills C-1)</p>
    </div>
    <div style="font-size: 0.8rem; color: #64748b;">
      Vertical Slice 01 · Playable Browser Build
    </div>
  </div>
  <div class="game-wrapper">
    {widget_html}
  </div>
</body>
</html>"""

out_file = Path(__file__).resolve().parent / "index.html"
out_file.write_text(full_html, encoding="utf-8")
print(f"Generated standalone index.html at: {out_file} (Bytes: {len(full_html)})")
