# Clip Reviewer & Voice Dictation Studio

A local, lightweight, keyboard-first video review and voice dictation workbench for curating documentary archives. Built to review the 201 video clips of *The Last Year* without switching between VLC, Windows Explorer, and Notepad.

---

## Quick Start

1. Start the local server:
   ```bash
   python app.py
   ```
2. Open your browser to:
   ```
   http://localhost:8765
   ```
3. Use keyboard controls to watch, scrub, dictate notes, and triage clips.

---

## Keyboard Controls

| Key | Action |
| :--- | :--- |
| `Space` | Play / Pause |
| `←` / `→` | Jump back / forward 3 seconds |
| `Shift + ←` / `Shift + →` | Step 1 frame backward / forward |
| `T` | Insert current playback timecode (e.g. `[00:14]`) into notes |
| `R` | Toggle live voice dictation (microphone) |
| `1` | Tag as Anchor / Must-Use A-Roll |
| `2` | Tag as B-Roll / Visual Counterpoint |
| `3` | Tag as Audio-Only / Voiceover |
| `4` | Tag as Discard / Skip |
| `[` / `]` | Decrease / Increase playback speed (0.75x, 1x, 1.25x, 1.5x, 2x) |
| `Ctrl + Enter` | Save note, mark reviewed, and advance to next clip |
| `Esc` | Unfocus note area to return to playback shortcuts |

---

## Persistence

- Notes and review status are saved to:
  `C:\Users\admir\Desktop\videos\The_Last_Year_Clips\clip_notes.json`
- A readable Markdown log is automatically updated at:
  `C:\Users\admir\Desktop\videos\The_Last_Year_Clips\CLIP_NOTES.md`
- A local backup is maintained in `data/clip_notes.json`.
