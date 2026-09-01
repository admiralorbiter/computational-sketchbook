# Phase 1C Manual Test Checklist

## Preset Availability Test

### Setup
1. Start Flask server: `python app.py`
2. Open Operator UI: `http://localhost:5000/operator`
3. Open Show View: `http://localhost:5000/show`

### Test Steps
- [ ] All 7 presets visible in Preset Selector grid:
  - [ ] Lissajous Curves
  - [ ] Polar Roses
  - [ ] Spirograph
  - [ ] Digits Rain
  - [ ] Ulam Spiral
  - [ ] Conway's Life
  - [ ] Mandelbrot Set
- [ ] Each preset can be started from Preset Selector
- [ ] Each preset renders correctly on Show View

### Expected Result
All 7 presets are available and functional.

---

## Performance Test (55+ fps per preset)

### Test Each Preset
For each preset, verify FPS sustains 55+ fps:

1. **Lissajous**
   - [ ] Start Lissajous preset
   - [ ] Monitor FPS for 30 seconds
   - [ ] FPS should remain 55+

2. **Polar Roses**
   - [ ] Start Polar Roses preset
   - [ ] Monitor FPS for 30 seconds
   - [ ] FPS should remain 55+

3. **Spirograph**
   - [ ] Start Spirograph preset
   - [ ] Monitor FPS for 30 seconds
   - [ ] FPS should remain 55+

4. **Digits Rain**
   - [ ] Start Digits Rain preset
   - [ ] Monitor FPS for 30 seconds
   - [ ] FPS should remain 55+

5. **Ulam Spiral**
   - [ ] Start Ulam Spiral preset
   - [ ] Monitor FPS for 30 seconds
   - [ ] FPS should remain 55+

6. **Conway's Life**
   - [ ] Start Conway's Life preset
   - [ ] Monitor FPS for 30 seconds
   - [ ] FPS should remain 55+

7. **Mandelbrot**
   - [ ] Start Mandelbrot preset
   - [ ] Monitor FPS for 30 seconds
   - [ ] FPS should remain 55+ (may be lower on slower hardware)

### Expected Result
Each preset maintains minimum 55 fps for 30 seconds.

---

## Preset Switching Test (< 500ms)

### Test Steps
- [ ] Start Lissajous preset
- [ ] Click "Start Preset" on Polar Roses
- [ ] Measure time from click to visual change
- [ ] Should be < 500ms
- [ ] Repeat for all preset combinations

### Test Scenarios
1. **Simple → Simple** (Lissajous → Polar Roses)
   - [ ] Switch time < 500ms

2. **Simple → Medium** (Lissajous → Digits Rain)
   - [ ] Switch time < 500ms

3. **Medium → Complex** (Digits Rain → Mandelbrot)
   - [ ] Switch time < 500ms

4. **Complex → Simple** (Mandelbrot → Lissajous)
   - [ ] Switch time < 500ms

### Expected Result
All preset switches complete in < 500ms.

---

## Theme Consistency Test

### Test Steps
- [ ] Start each preset in sequence
- [ ] Verify all presets use theme colors:
  - [ ] Lissajous uses accent green
  - [ ] Polar Roses uses accent cyan
  - [ ] Spirograph uses accent green
  - [ ] Digits Rain uses accent green
  - [ ] Ulam Spiral uses accent cyan
  - [ ] Conway's Life uses accent green
  - [ ] Mandelbrot uses accent cyan (or color cycle)
- [ ] No hardcoded colors visible
- [ ] Colors match Neon Chalkboard theme

### Expected Result
All presets use theme colors consistently.

---

## Performance Guardrails Test

### Test Steps
1. **Trigger Performance Warning**
   - [ ] Start Mandelbrot preset with high maxIter (e.g., 500)
   - [ ] Monitor FPS
   - [ ] If FPS drops below 55 for 3 seconds:
     - [ ] Performance warning should appear
     - [ ] Complexity should be reduced automatically
     - [ ] FPS should recover

2. **Verify Guardrail Actions**
   - [ ] Check console for "Performance guardrails activated" message
   - [ ] Verify parameters were reduced (density, maxIter, etc.)
   - [ ] FPS should improve after reduction

### Expected Result
Performance guardrails activate when FPS < 55 for 3 seconds and reduce complexity automatically.

---

## Duration Control Test

### Test Steps
1. **Auto-Advance Test**
   - [ ] Start preset with duration: 5000 (5 seconds)
   - [ ] Scene should auto-stop after 5 seconds
   - [ ] Verify scene stops automatically

2. **Infinite Duration Test**
   - [ ] Start preset with duration: 0 (infinite)
   - [ ] Scene should continue until manually stopped
   - [ ] Verify scene does not auto-stop

### Expected Result
Duration control works correctly for both finite and infinite durations.

---

## Transition Test

### Test Steps
1. **Cut Transition**
   - [ ] Start Lissajous preset
   - [ ] Switch to Polar Roses with transition: 'cut'
   - [ ] Verify instant switch (no fade)

2. **Fade Transition**
   - [ ] Start Spirograph preset
   - [ ] Switch to Digits Rain with transition: 'fade:300'
   - [ ] Verify smooth fade transition (~300ms)

3. **Crossfade Transition**
   - [ ] Start Ulam Spiral preset
   - [ ] Switch to Conway's Life with transition: 'crossfade:500'
   - [ ] Verify crossfade effect (~500ms)

### Expected Result
All transition types work correctly and complete within specified duration.

---

## Notes
- Record any performance issues or optimization needs
- Note any visual inconsistencies or bugs
- Document browser and hardware used for testing
- Test on different screen resolutions if possible

