# UI_Style_Guide

## Core principles
- Clarity beats realism.
- Never require color alone to convey critical info.
- Always show “why” (stall reason, trigger reason, failure reason).

## Icon language
- Receptor: hex/antenna motif
- Relay: node/triangle motif
- Effector: circle/burst motif
- Shipping: vesicle bubble motif
- Infection: blot/spore motif
- Stress: crack/heat motif

## Overlays
- Circuit view:
  - Nodes simplified
  - Edges show direction arrows
  - Highlight active path when a trigger fires
- Logistics view:
  - Tracks thickened
  - Vesicles bright + show ETA
  - Congestion pulses + tooltip says why
- Infection view:
  - Show spread edges and sources
  - Infection nodes are high-contrast targets

## Tooltips (minimum content)
- Name + category
- What it does (1 line)
- Costs: ATP per trigger, stress gain
- Cooldowns and ranges
- Any special conditions

## Accessibility
- Text scaling options
- Colorblind palettes or patterns
- Optional “outline mode” for infection overlay
