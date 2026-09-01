# QA_Test_Plan (Practical)

## Must-pass smoke tests (MVP)
1. Start run, complete wave 1 without crashes.
2. Place module, confirm it is not active until delivered.
3. Cancel a queued build, confirm refund behavior matches design.
4. Vesicle delivery reroutes when track removed/blocked.
5. Circuit trigger fires only when condition met.
6. Relay gate prevents spam.
7. Infection spreads deterministically given fixed seed (optional).
8. Cleanse cannot reduce infection below zero.
9. Infection reaching mitochondrion causes the intended crisis effect.
10. Adaptation triggers after N waves and is announced to player.
11. Pause fully freezes simulation timers.
12. Speed settings do not break physics or timers.
13. Lose condition triggers reliably on nucleus HP=0.

## Regression areas (watch list)
- Graph edges broken when node removed mid-wave
- Double-trigger bugs from overlapping sensors
- Refund exploits (queue cancel, delivery cancel)
- Performance spikes from infection spread / pathfinding

## Test harness recommendations
- Debug panel:
  - spawn enemy type
  - add ATP
  - toggle stress
  - set infection coverage
  - force adaptation pick
- Run seed display + replay same seed
