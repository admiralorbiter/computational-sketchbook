# Sprint 1 Manual Test Scenarios

This document outlines manual test scenarios for validating Sprint 1 functionality. These tests should be performed after implementing the core systems to ensure everything works as expected.

## Test Environment Setup

1. **Run the game**: `python main.py`
2. **Start the game**: Press SPACE to enter playing state
3. **Debug mode**: Press F3 to toggle debug overlay (shows FPS, entity counts, paths)

## Test Scenarios

### 1. Basic Movement Test

**Objective**: Verify kids spawn and move autonomously

**Steps**:
1. Start the game
2. Observe 10 kids spawning with different colors
3. Watch kids move around the map
4. Verify kids are moving in different directions

**Expected Results**:
- ✅ 10 kids spawn with different colors
- ✅ Kids move autonomously around the map
- ✅ Kids change direction and target houses
- ✅ No kids get stuck in one position

**Pass Criteria**: All kids are moving and changing behavior

---

### 2. House Quality System Test

**Objective**: Verify house quality system works correctly

**Steps**:
1. Start the game
2. Observe houses with different colors and letters
3. Count houses by quality level
4. Verify quality distribution

**Expected Results**:
- ✅ Houses have different colors (gray, brown, gold)
- ✅ Houses display quality letters (A, B, C)
- ✅ Quality distribution follows configuration
- ✅ High-quality houses (gold C) are less common than low-quality (gray A)

**Pass Criteria**: Visual quality system is clear and follows expected distribution

---

### 3. Pathfinding Test

**Objective**: Verify kids navigate around houses using pathfinding

**Steps**:
1. Start the game
2. Press F3 to enable debug overlay
3. Observe green lines showing kid paths
4. Watch kids move around houses instead of through them
5. Look for red dots showing current waypoints

**Expected Results**:
- ✅ Kids follow curved paths around houses
- ✅ Green lines show planned paths
- ✅ Red dots show current waypoints
- ✅ Kids never walk through houses
- ✅ Paths are efficient and direct

**Pass Criteria**: All kids use pathfinding and avoid obstacles

---

### 4. Candy Dispensing Test

**Objective**: Verify candy system works correctly

**Steps**:
1. Start the game
2. Watch kids visit houses
3. Observe numbers above kids' heads
4. Count candy inventory changes
5. Verify different house qualities give different candy

**Expected Results**:
- ✅ Kids receive candy when visiting houses
- ✅ Numbers above kids show inventory counts
- ✅ Inventory counts increase over time
- ✅ High-quality houses give more/better candy
- ✅ Kids visit multiple houses

**Pass Criteria**: Candy system is functional and visible

---

### 5. Performance Test

**Objective**: Verify game maintains 60 FPS

**Steps**:
1. Start the game
2. Press F3 to show debug overlay
3. Observe FPS counter
4. Let game run for 30 seconds
5. Note any performance drops

**Expected Results**:
- ✅ FPS stays at 60 (or close to it)
- ✅ No significant frame drops
- ✅ Game runs smoothly
- ✅ Debug overlay shows consistent performance

**Pass Criteria**: Stable 60 FPS maintained

---

### 6. Stress Test

**Objective**: Test performance with more kids

**Steps**:
1. Modify `spawn_kids(20)` in `src/core/game.py` (line 166)
2. Restart the game
3. Observe performance with 20 kids
4. Press F3 to monitor FPS
5. Let run for 1 minute

**Expected Results**:
- ✅ Game still runs at 60 FPS
- ✅ All 20 kids are moving
- ✅ Pathfinding still works
- ✅ No crashes or freezes

**Pass Criteria**: Game handles 20 kids without performance issues

---

### 7. Camera System Test

**Objective**: Verify camera system works correctly

**Steps**:
1. Start the game
2. Observe world-to-screen conversion
3. Check that all entities are visible
4. Verify coordinate conversion accuracy

**Expected Results**:
- ✅ All houses and kids are visible on screen
- ✅ Entities appear in correct positions
- ✅ No entities are cut off or outside view
- ✅ World coordinates map correctly to screen

**Pass Criteria**: Camera system displays world correctly

---

### 8. Debug Overlay Test

**Objective**: Verify debug overlay functionality

**Steps**:
1. Start the game
2. Press F3 to toggle debug overlay
3. Observe debug information
4. Press F3 again to hide overlay
5. Verify overlay toggles correctly

**Expected Results**:
- ✅ F3 toggles debug overlay on/off
- ✅ Debug overlay shows FPS, entity counts
- ✅ Pathfinding paths are visible when overlay is on
- ✅ Overlay is readable and informative

**Pass Criteria**: Debug overlay works correctly

---

### 9. Edge Case Test

**Objective**: Test edge cases and error handling

**Steps**:
1. Start the game
2. Let it run for 5 minutes
3. Observe for any crashes or errors
4. Check for kids getting stuck
5. Verify no memory leaks

**Expected Results**:
- ✅ No crashes or errors
- ✅ Kids continue moving throughout test
- ✅ No kids get permanently stuck
- ✅ Memory usage remains stable

**Pass Criteria**: Game runs stably for extended periods

---

### 10. Visual Clarity Test

**Objective**: Verify visual elements are clear and distinguishable

**Steps**:
1. Start the game
2. Observe visual clarity
3. Check that kids and houses are distinguishable
4. Verify colors are appropriate
5. Check text readability

**Expected Results**:
- ✅ Kids and houses are clearly different
- ✅ Quality levels are visually distinct
- ✅ Inventory numbers are readable
- ✅ Pathfinding lines are visible but not distracting
- ✅ Color scheme is appropriate

**Pass Criteria**: Visual elements are clear and professional

---

## Test Results Summary

After completing all test scenarios, document the results:

### Passed Tests
- [ ] Basic Movement Test
- [ ] House Quality System Test
- [ ] Pathfinding Test
- [ ] Candy Dispensing Test
- [ ] Performance Test
- [ ] Stress Test
- [ ] Camera System Test
- [ ] Debug Overlay Test
- [ ] Edge Case Test
- [ ] Visual Clarity Test

### Failed Tests
- [ ] List any failed tests here

### Issues Found
- [ ] List any issues or bugs discovered

### Performance Notes
- [ ] Document any performance observations

### Recommendations
- [ ] List any recommendations for improvements

---

## Test Completion Criteria

Sprint 1 is considered complete when:

1. **All 10 test scenarios pass**
2. **Game runs at stable 60 FPS**
3. **Kids move autonomously and visit houses**
4. **Pathfinding works correctly**
5. **Candy system is functional**
6. **No crashes or major bugs**
7. **Visual elements are clear and professional**

## Test Data

### Expected Entity Counts
- **Houses**: 18 (with quality distribution)
- **Kids**: 10 (with different colors)
- **FPS**: 60 (stable)

### Expected Behaviors
- **Kids**: Move autonomously, visit houses, collect candy
- **Houses**: Dispense candy based on quality
- **Pathfinding**: Kids navigate around obstacles
- **Camera**: World coordinates map to screen correctly

### Performance Targets
- **Frame Rate**: 60 FPS
- **Update Time**: < 16.67ms per frame
- **Memory Usage**: Stable (no leaks)
- **CPU Usage**: Reasonable for 10-20 entities
