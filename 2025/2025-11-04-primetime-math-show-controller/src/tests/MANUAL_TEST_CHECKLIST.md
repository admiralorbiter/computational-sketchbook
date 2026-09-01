# Phase 1B Manual Test Checklist

## FPS Performance Test (60 seconds)

### Setup
1. Start Flask server: `python app.py`
2. Open Show View: `http://localhost:5000/show`
3. Open Operator UI: `http://localhost:5000/operator` (in separate window)

### Test Steps
- [ ] Start Lissajous scene from Operator UI
- [ ] Monitor FPS counter in Show View for 60 seconds
- [ ] FPS should remain between 55-60 fps
- [ ] No frame drops or stuttering observed

### Expected Result
FPS sustains 60fps (or monitor refresh rate) for full 60 seconds.

---

## Memory Leak Test (5 minutes)

### Setup
1. Open Chrome DevTools (F12)
2. Navigate to Performance tab
3. Click "Record" button

### Test Steps
- [ ] Start Lissajous scene from Operator UI
- [ ] Let scene run for 5 minutes continuously
- [ ] Stop recording in DevTools
- [ ] Check memory usage graph in Performance tab

### Expected Result
- Memory usage should stabilize after initial load (first 10-20 seconds)
- No continuous upward trend indicating memory leaks
- Memory should remain relatively stable throughout 5-minute run

---

## Parameter Update Performance Test

### Setup
- Lissajous scene should be running

### Test Steps
- [ ] Rapidly move parameter sliders (a, b, delta, speed)
- [ ] Monitor FPS counter during slider movements
- [ ] Test multiple rapid parameter changes

### Expected Result
- FPS should remain stable at 55-60fps during parameter updates
- No stuttering or frame drops when sliders move
- Visual updates should be smooth and responsive

---

## Edge Case Performance Test

### Test Scenarios
Test these parameter combinations and verify FPS stays at 55+:

1. **Low Frequency**
   - [ ] a=1, b=1
   - [ ] FPS should remain 55+

2. **High Frequency**
   - [ ] a=10, b=10
   - [ ] FPS should remain 55+

3. **High Speed**
   - [ ] speed=3
   - [ ] FPS should remain 55+

4. **Low Speed**
   - [ ] speed=0.1
   - [ ] FPS should remain 55+

5. **Extreme Delta**
   - [ ] delta=6.28 (2π)
   - [ ] FPS should remain 55+

### Expected Result
All parameter combinations should maintain 55+ fps without performance degradation.

---

## Error Handling Test

### Test Scenarios
- [ ] Start scene with invalid parameters (handled by validation)
- [ ] Verify error messages appear in console (not to user)
- [ ] Verify scene still starts with default/validated parameters
- [ ] Test canvas initialization failure scenarios (if possible)

---

## Notes
- All tests should be run on a consistent hardware setup
- Record any deviations from expected behavior
- Note browser and version used for testing
- Document any performance issues or optimizations needed

