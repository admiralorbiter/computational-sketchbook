# User Stories

> Acceptance criteria are included for each story. Developer and future networking stories follow the player stories.

---

## Player Stories

### Story 1 — Responsive Movement
As a player, I want my character to move immediately when I press left/right so I feel precise control.

**Acceptance Criteria**
- pressing movement input changes velocity within the next update step
- character facing updates correctly
- stopping movement decelerates predictably
- movement feels consistent across both players

### Story 2 — Jump and Air Control
As a player, I want to jump and steer in the air so movement is expressive.

**Acceptance Criteria**
- jump launches character upward reliably
- air movement is weaker than grounded movement but still responsive
- landing restores grounded actions
- double-trigger bugs do not occur on held jump input

### Story 3 — Dash
As a player, I want a dash for fast repositioning so spacing battles feel dynamic.

**Acceptance Criteria**
- dash triggers from valid states only
- dash covers consistent distance/time
- dash has cooldown or commitment window
- dash cannot be spammed infinitely without rule enforcement

### Story 4 — Light and Heavy Attacks
As a player, I want light and heavy attacks with different speed/power tradeoffs so combat has depth.

**Acceptance Criteria**
- light attacks start faster than heavy attacks
- heavy attacks have higher commitment and stronger reward
- attacks cannot overlap into invalid states
- move timing is defined by data

### Story 5 — Blocking
As a player, I want to guard against attacks so I have defensive counterplay.

**Acceptance Criteria**
- guard reduces or negates frontal attacks
- heavy attacks or specific moves can pressure/break guard
- guarding uses a rule set consistent across characters
- UI/state feedback shows successful guard behavior

### Story 6 — Special Identity
As a player, I want each character to have signature powers so they feel unique.

**Acceptance Criteria**
- each character has at least two specials
- each special has distinct gameplay purpose
- resource cost is visible and enforced
- abilities are identifiable with placeholder art/VFX

### Story 7 — Match Completion
As a player, I want rounds to end and restart clearly so local matches feel complete.

**Acceptance Criteria**
- KO condition triggers result state
- round count updates
- players reset to spawn positions
- health/resource reset behavior matches design

### Story 8 — Onboarding
As a player, I want to understand the controls quickly so I can start fighting without confusion.

### Story 9 — Character Distinction
As a player, I want characters to feel distinct so my choice matters.

### Story 10 — Visual Clarity
As a player, I want visual clarity on attacks and specials so I can react.

### Story 11 — Readable UI
As a player, I want health and resource UI to be readable so I can make decisions.

### Story 12 — Easy Rematch
As a player, I want rematches to be easy so local play can continue quickly.

---

## Developer Stories

### Story D1 — Developer Debugging
As a developer, I want debug overlays so I can inspect gameplay state.

**Acceptance Criteria**
- can toggle hitboxes/hurtboxes
- can view current state and frame timer
- can view resource/health values
- can reset match quickly

### Story D2 — Fast Iteration
As a developer, I want the game to run quickly in dev mode so iteration is fast.

### Story D3 — Modular Systems
As a developer, I want systems to be modular so I can change mechanics without breaking unrelated features.

### Story D4 — Data-Driven Tuning
As a developer, I want gameplay values stored in data definitions so tuning is faster than rewriting logic.

### Story D5 — Reproducible Bugs
As a developer, I want input logs and frame data so I can reproduce gameplay issues.

### Story D6 — Replay-Friendly Architecture
As a developer, I want replay-friendly architecture so multiplayer expansion is less risky later.

### Story D7 — Decoupled Rendering
As a developer, I want gameplay and rendering separated so network synchronization does not require major rewrites.

### Story D8 — Compact Input
As a developer, I want compact input representation so local simulation can later inform online protocols.
