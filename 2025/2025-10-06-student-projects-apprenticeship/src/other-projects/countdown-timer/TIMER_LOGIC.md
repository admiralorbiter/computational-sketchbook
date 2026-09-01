# Timer Logic

## Core calculations
1. `now = Date.now()`
2. `delta = target - now` (ms)
3. Convert to days/hours/minutes/seconds
4. Clamp negative values; show “Event Ended” at zero

## Update loop
- Single `setInterval` to update all visible timers (e.g., every 1000 ms)
- Batch DOM updates and pause when tab inactive
- Handle DST and leap years; store and compute in ISO strings

## Advanced
- Recurring events; chains (sequential)
- Notifications at configured thresholds (1w/1d/1h)
- Time zone and DST safeguards (use local display)
