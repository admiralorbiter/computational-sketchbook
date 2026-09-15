import os
import sys
import json
import re
import urllib.parse
import mimetypes
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PORT = 8765
CLIPS_DIR = r"C:\Users\admir\Desktop\videos\The_Last_Year_Clips"
APP_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_JSON = os.path.join(CLIPS_DIR, "clip_notes.json")
NOTES_MD = os.path.join(CLIPS_DIR, "CLIP_NOTES.md")
BACKUP_JSON = os.path.join(APP_DIR, "data", "clip_notes.json")

def load_notes():
    if os.path.exists(NOTES_JSON):
        try:
            with open(NOTES_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    if os.path.exists(BACKUP_JSON):
        try:
            with open(BACKUP_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_notes(notes):
    os.makedirs(os.path.dirname(NOTES_JSON), exist_ok=True)
    with open(NOTES_JSON, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)
    
    os.makedirs(os.path.dirname(BACKUP_JSON), exist_ok=True)
    with open(BACKUP_JSON, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)
    
    render_notes_markdown(notes)

def render_notes_markdown(notes):
    lines = [
        "# The Last Year — Curated Clip Notes & Editorial Log",
        "",
        f"Total clips reviewed: {len([k for k, v in notes.items() if v.get('status') == 'reviewed'])}",
        "",
        "---",
        ""
    ]
    
    sorted_items = sorted(
        notes.items(),
        key=lambda kv: (kv[1].get('date', '9999-99-99'), kv[0])
    )
    
    tag_labels = {
        "anchor": "[ANCHOR / MUST-USE A-ROLL]",
        "broll": "[B-ROLL / VISUAL COUNTERPOINT]",
        "audio": "[AUDIO-ONLY / VOICEOVER]",
        "discard": "[DISCARD / SKIP]"
    }
    
    for filename, data in sorted_items:
        tag = tag_labels.get(data.get("tag"), "[UNTAGGED]")
        folder = data.get("folder", "")
        note_text = data.get("notes", "").strip()
        status = data.get("status", "unreviewed")
        
        lines.append(f"## {filename}")
        lines.append(f"- Folder: `{folder}`")
        lines.append(f"- Priority / Tag: {tag}")
        lines.append(f"- Status: {status.upper()}")
        if note_text:
            lines.append("- Editorial Notes & Dictation:")
            for n_line in note_text.splitlines():
                lines.append(f"  > {n_line}")
        lines.append("")
    
    with open(NOTES_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def get_all_clips():
    clips = []
    notes = load_notes()
    if not os.path.exists(CLIPS_DIR):
        return clips
    
    for folder in sorted(os.listdir(CLIPS_DIR)):
        folder_path = os.path.join(CLIPS_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        for fname in sorted(os.listdir(folder_path)):
            if fname.lower().endswith(('.mp4', '.mov', '.mkv')):
                m = re.match(r"^(\d{4}-\d{2}-\d{2})", fname)
                date = m.group(1) if m else ""
                
                note_data = notes.get(fname, {})
                clips.append({
                    "id": f"{folder}__{fname}",
                    "folder": folder,
                    "filename": fname,
                    "date": date,
                    "url": f"/video/{urllib.parse.quote(folder)}/{urllib.parse.quote(fname)}",
                    "status": note_data.get("status", "unreviewed"),
                    "tag": note_data.get("tag", ""),
                    "notes": note_data.get("notes", "")
                })
    return clips

class ReviewerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=APP_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        if path == "/api/clips":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            clips = get_all_clips()
            self.wfile.write(json.dumps(clips, ensure_ascii=False).encode("utf-8"))
            return
            
        elif path == "/api/notes":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            notes = load_notes()
            self.wfile.write(json.dumps(notes, ensure_ascii=False).encode("utf-8"))
            return

        elif path.startswith("/video/"):
            rel_path = urllib.parse.unquote(path[len("/video/"):])
            full_path = os.path.join(CLIPS_DIR, rel_path)
            self.serve_video_range(full_path)
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/notes":
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode('utf-8'))
                filename = data.get("filename")
                if not filename:
                    self.send_error(400, "Missing filename")
                    return
                notes = load_notes()
                notes[filename] = {
                    "folder": data.get("folder", ""),
                    "date": data.get("date", ""),
                    "tag": data.get("tag", ""),
                    "notes": data.get("notes", ""),
                    "status": data.get("status", "reviewed"),
                    "updated_at": data.get("updated_at", "")
                }
                save_notes(notes)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "notes": notes}).encode("utf-8"))
            except Exception as e:
                self.send_error(500, str(e))
            return
            
        self.send_error(404)

    def serve_video_range(self, filepath):
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            self.send_error(404, "File not found")
            return
            
        file_size = os.path.getsize(filepath)
        mime_type, _ = mimetypes.guess_type(filepath)
        if not mime_type:
            mime_type = "video/mp4"
            
        range_header = self.headers.get("Range")
        if range_header:
            m = re.match(r"bytes=(\d+)-(\d*)", range_header)
            if m:
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else file_size - 1
                end = min(end, file_size - 1)
                content_length = (end - start) + 1
                
                self.send_response(206)
                self.send_header("Content-Type", mime_type)
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                self.send_header("Content-Length", str(content_length))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                
                with open(filepath, "rb") as f:
                    f.seek(start)
                    chunk_size = 64 * 1024
                    remaining = content_length
                    while remaining > 0:
                        to_read = min(chunk_size, remaining)
                        buf = f.read(to_read)
                        if not buf:
                            break
                        try:
                            self.wfile.write(buf)
                        except (ConnectionResetError, BrokenPipeError):
                            break
                        remaining -= len(buf)
                return
                
        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(file_size))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        
        with open(filepath, "rb") as f:
            chunk_size = 64 * 1024
            while True:
                buf = f.read(chunk_size)
                if not buf:
                    break
                try:
                    self.wfile.write(buf)
                except (ConnectionResetError, BrokenPipeError):
                    break

def run_server():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), ReviewerHandler)
    print(f"Clip Reviewer Server running at http://localhost:{PORT}")
    print(f"Reading media from: {CLIPS_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()

if __name__ == "__main__":
    run_server()
