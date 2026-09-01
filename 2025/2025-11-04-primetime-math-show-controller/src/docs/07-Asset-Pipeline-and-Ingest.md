# Asset Pipeline & Ingest

## Folders
```
/assets
  /photos
  /videos
  /music
  /logos
/themes
/config
```

## File Watch & Preprocess
- **watchdog** monitors asset folders.
- **Images**: EXIF orientation fix, scale to max 2200px (longest edge), thumbnail generation, content hash.
  - Formats: JPEG, PNG
  - Max dimensions: 6000x6000 pixels (auto-scaled if larger)
  - Max file size: 50 MB per image
- **Videos**: ffprobe metadata (codec/duration); validate MP4 H.264/AAC; first-frame thumbnail.
  - Video codec: H.264 (baseline, main, or high profile)
  - Audio codec: AAC or MP3
  - Max resolution: 1920x1080 (will scale if larger)
  - Max file size: 500 MB
- **Audio/Music**: metadata extraction; validate MP3/M4A; optional loudness measurement (future).
  - Formats: MP3, M4A (AAC)
  - Bitrate: 128-320 kbps (warning if < 128 kbps)
  - Max file size: 100 MB

## Caching
- SQLite tables: `assets`, `thumbnails`, `metadata`.
- Preload queue: next scene's textures / first video frame prepared before switch.

## Validation Error Codes

**Video Errors:**
- `INVALID_CODEC` - Unsupported video/audio codec (not H.264/AAC/MP3)
- `RESOLUTION_TOO_HIGH` - Exceeds 1920x1080 (warning only, will scale)
- `FILE_TOO_LARGE` - Exceeds 500 MB
- `CORRUPT` - File unreadable or truncated
- `MISSING_AUDIO` - Video has no audio track (warning, not error)

**Image Errors:**
- `INVALID_FORMAT` - Not JPEG or PNG
- `CORRUPT` - Image unreadable or truncated
- `FILE_TOO_LARGE` - Exceeds 50 MB
- `DIMENSIONS_TOO_LARGE` - Exceeds 6000x6000 (will auto-scale, but warn)

**Audio Errors:**
- `INVALID_FORMAT` - Not MP3 or M4A
- `LOW_BITRATE` - Below 128 kbps (warning, not error)
- `FILE_TOO_LARGE` - Exceeds 100 MB
- `CORRUPT` - File unreadable

See `14-Error-Handling-and-Validation.md` for detailed validation logic and fallback behavior.

## Constraints
- Avoid repeats in slideshow for N minutes.
- Prefer newer photos first (weighted selection).

