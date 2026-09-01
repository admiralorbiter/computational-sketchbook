# Operator UI Design

## Layout
- **Left:** Asset bins (Videos, Photos, Music, Logos) with thumbnails.
- **Center:** Timeline track (cards with scene type + duration).
- **Right:** Inspector & Live Controls.

## Live Controls (always visible)
- **Transport:** Play/Pause, Prev/Next, Hold/Resume, Blackout, Volume.
- **Cues:** Countdown (10/5/3), Confetti, Show Text (quick input), JumpTo(select).
- **Status:** FPS, connected, current item/timecode, 'next up'.

## Inspector
- Scene-specific params (sliders & toggles).
- Theme selection dropdown (Neon Chalkboard default).
- Transition pickers (fade/cross/cut + ms).

## Hotkeys
- Space: Play/Pause
- ← / →: Prev / Next
- C: Countdown
- B: Blackout
- F: Confetti

## Validation & Safety
- Warnings for missing files / unsupported codecs.
- Preview mini-window (mirrors Show View).
- Autosave with undo/redo.
