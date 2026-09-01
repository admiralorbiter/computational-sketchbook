# PRD — Parasite Protocol

## 1) High concept
**Parasite Protocol** is a 2D systems-driven “tower defense + infection survival” game set inside a single living cell. The player **manufactures** defenses (protein modules), **ships** them via vesicles over cytoskeleton tracks, and wires **signal circuits** (receptors → relays → effectors) to respond to waves of intruders. Infection spreads dynamically and enemies adapt to the player’s strategy.

**One-sentence pitch:** A living tower defense where defenses are expressed, shipped, and triggered by biological signaling—contain the breach before the cell collapses.

## 2) Design pillars
1. Logistics is gameplay (manufacture + delivery, not instant build).
2. Reactive circuits (event-driven defenses).
3. Containment pressure (infection overlay attacks economy + wiring).
4. Meaningful risk (stress tradeoffs).
5. Adaptation (selection pressure counters overused tactics).

## 3) Target & constraints
- Platform: PC first
- Session length: 20–45 min per run
- Camera: top-down 2D arena (single cell screen)
- Run structure: waves + short recovery choices

## 4) Success criteria (MVP)
- Players can complete a full run (8 waves + 1 boss) with at least 3 viable strategies.
- Manufacturing + delivery meaningfully changes decisions vs standard TD.
- Circuit view is readable and helps debugging (“why did this trigger?”).
- Infection forces mid-wave triage (not ignorable, not overwhelming).
- Adaptation messaging is clear and fair.

## 5) Core loop
### Moment-to-moment (10–20s)
Inspect threats → queue builds → place/wire circuits → route shipping → contain infection → use abilities.

### Run loop
Wave → Incursion → Recovery choice → Upgrade → Next wave.

## 6) Key systems (summary)
- Arena: membrane ring, organelles, cytoplasm
- Economy: ATP + blocks, stress, membrane integrity
- Manufacturing: ribosome queue → ER/Golgi assembly → vesicle shipping
- Tracks: microtubules + actin; route shipping + soft enemy control
- Circuits: receptors → relays → effectors; event-driven
- Infection overlay: spreading hazard + nodes
- Adaptation: weighted counters based on recent player strategy
- Between waves: gene cards

## 7) MVP scope
- 1 cell class
- 10 enemies (3 families)
- 12 modules (4 receptors, 4 relays, 4 effectors)
- Infection overlay (simple spread + cleanse)
- Manufacturing queue + shipping
- Circuit wiring (basic connect + visualize)
- 8 waves + 1 boss
- 20 gene cards

## 8) Out of scope for MVP (parked)
- Campaign/scenario scripting
- Tissue/multi-cell mode
- Online leaderboards
- Full codex art + lore
