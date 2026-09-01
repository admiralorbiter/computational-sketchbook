# UI, UX, and HUD

## 1. UI Philosophy

The UI should be readable, calm, and informative. It should help the player think like an engineer without drowning them in noise.

Guiding rules:

- show the numbers that matter
- explain risk before launch
- explain failure after launch
- keep screen regions stable and predictable
- use plain, reusable widgets over decorative complexity

## 2. Screens and Menus

## 2.1 Main Menu
Purpose: entry point into the game.

Recommended options:
- Start / Continue
- Mission Select
- Sandbox
- Settings
- Quit

Optional flavor:
- subtitle text or mission log tone under the title

## 2.2 Mission Select
Purpose: pick a target and understand expectations.

Required information:
- mission name
- one-sentence description
- objectives
- unlocked / locked state
- reward or unlock preview if used

## 2.3 Pause Menu
Purpose: safe interruption during flight.

Options:
- Resume
- Restart Mission
- Return to Builder
- Return to Main Menu

## 2.4 Debrief Screen
Purpose: convert outcomes into learning.

Must include:
- success or failure headline
- objective completion list
- max altitude
- peak speed
- stage usage summary
- failure hints or likely cause
- quick retry

## 3. Builder UI

The builder is one of the game’s most important screens. It should feel simple, mechanical, and quick.

### Interaction Model

Decision: click-to-add, stacked vertically.

The player selects a part from the palette and clicks a valid attachment point to place it. The rocket grows vertically, which matches the 2D launch metaphor directly. No drag-and-drop for MVP — it adds implementation cost without proportional player value at this scope. Revisit if playtest feedback strongly argues for it.

### Builder Keybindings
- **Click**: Select parts from palette or canvas.
- **Enter**: Place highlighted palette part into canvas.
- **Delete / Backspace**: Remove selected part from canvas.
- **Left/Right Arrow**: Push the selected part forward or backward in the staging sequence.
- **L**: Quick-launch the assembled rocket.
- **R**: Clear canvas entirely.
- **Escape**: Return to Main Menu.

### Auto-Staging Model
For the MVP Builder, when a part is added, it is automatically assigned to Stage 0. The player can manually select individual parts in the visual canvas and nudge them (Left/Right) to higher or lower stages.

### Center Canvas Schematic
Instead of a text list, the center canvas renders a block-out silhouette of the rocket. Parts are sized proportionately to their mass/category (Command at top, Tanks in middle, Engines at bottom). Hovering highlights parts in yellow, selecting highlights them in green.

## 3.1 Layout Regions

### Left panel — Parts Palette
Contains categories and parts list.

Should show:
- part name
- icon or silhouette
- key stats at a glance
- category filter if needed

### Center — Build Canvas
Shows the assembled rocket in an uncluttered vertical workspace.

Should support:
- selection
- add/remove part
- clear snap visualization
- simple pan/zoom if needed

### Right panel — Part / Rocket Inspector
Shows details for either the selected part or overall rocket.

Should include:
- mass
- fuel
- thrust
- drag
- role or warnings

### Bottom or side panel — Staging List
Shows stage order and lets the player move actions up or down.

### Launch area
Should include:
- launch button
- validation warnings
- quick summary metrics

## 3.2 Builder Metrics

The builder should surface these early:

- total mass
- dry mass
- fuel mass
- current stage count
- estimated thrust-to-weight ratio at launch
- estimated delta-v or simplified capability rating

## 3.3 Validation Feedback

Examples of warnings:
- no command pod
- no active engine in launch stage
- launch TWR too low
- parachute present but unreachable after staging
- final stage has no fuel

Warnings should be grouped by severity:
- error: cannot launch or design is structurally invalid
- warning: launchable but risky or obviously flawed
- info: optional hints

## 4. Flight HUD

The flight HUD should be compact, stable, and readable at speed.

## 4.1 Essential Data

- altitude
- speed
- vertical speed
- throttle
- current stage
- fuel remaining
- apoapsis
- periapsis
- mission objective summary

## 4.2 Suggested Screen Placement

### Top-left
Core flight telemetry:
- altitude
- speed
- vertical speed

### Top-right
Mission and state info:
- objective summary
- warning state
- stable orbit indicator if relevant

### Bottom-left
Stage and fuel info:
- current stage label
- engine state
- fuel bars

### Bottom-right
Controls and map access:
- stage button
- map toggle
- pause

## 4.3 Flight Feedback

Examples:
- “Stage armed”
- “Fuel depleted”
- “Periapsis below atmosphere”
- “Launch TWR insufficient”
- “Stable orbit achieved”

Use short event banners or log lines, not giant interruptive popups.

## 5. Map UI

The map exists to make orbital thinking legible.

Must show:
- planet body
- atmosphere boundary
- current trajectory
- apoapsis / periapsis markers
- vessel position
- target orbit if relevant

Optional later:
- planned burn markers
- future path preview at different throttle or stage conditions

## 6. Visual Hierarchy

### Highest priority visual elements
- rocket position and movement
- stage controls
- altitude / speed / orbit metrics
- mission status

### Lower priority
- decorative framing
- background art
- nonessential labels

## 7. UX Conventions

Recommended conventions:

- same hotkeys everywhere sensible
- consistent button placement across screens
- all critical actions visible, not hidden behind mode changes
- tooltips for unfamiliar stats
- clear hover and selected states

## 8. Accessibility / Readability Considerations

- avoid tiny fonts
- avoid low-contrast UI
- avoid overusing color as the only indicator
- keep panel density modest
- use stable numeric formatting so values do not jitter visually too much

## 9. Developer UI

Separate developer-facing tools from player-facing UI.

Developer tools can be more raw and information-dense.

Potential dev widgets:
- sim time scale
- atmosphere multiplier
- gravity multiplier
- stage force trigger
- position / velocity editor
- preset rocket selector

## 10. UI Delivery Order

Build in this order:

1. minimal HUD for the hardcoded rocket prototype
2. debug overlay and event line
3. builder shell layout
4. staging list and validation messages
5. mission select and debrief screens
6. map screen
7. polish pass and consistency pass
