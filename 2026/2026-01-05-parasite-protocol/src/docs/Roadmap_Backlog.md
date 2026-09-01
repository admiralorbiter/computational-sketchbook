# Roadmap_Backlog — Implementation Order

## Phase 0 — Skeleton (foundation)
- Entity/component base
- Time step / pause / speed control
- Map renderer + collision / navigation primitives
- Basic UI framework (pan/zoom, selection, tooltips)

## Phase 1 — Combat basics
- Enemy spawner + movement
- Damage + HP + death
- Basic “membrane breach” mechanic
- Nucleus HP and lose condition

## Phase 2 — Placement and modules
- Placement rules (membrane vs interior)
- Module base class (cost, cooldown, radius)
- 2 receptors + 2 effectors (temporary direct-fire ok for testing)

## Phase 3 — Manufacturing + shipping
- Ribosome queue (slots, timers)
- ER/Golgi assembly step
- Vesicle units + delivery pathing
- Delivery UI (ETA, stalled state)

## Phase 4 — Tracks
- Track placement tool
- Vesicle routing along tracks
- Track repair and infection slowdown hooks

## Phase 5 — Circuits
- Circuit graph model (nodes, edges)
- Event bus + receptor triggers
- Relay transforms (amplify/split/gate/delay)
- Effector dispatch (payload + targeting)

## Phase 6 — Infection overlay
- Infection grid/field + spread rules
- Infection nodes + spawning rules
- Cleanse mechanics (mobile + effector)

## Phase 7 — Wave generator + recovery
- Threat budget wave builder
- Recovery screen w/ 3 gene cards
- Persist run state between waves

## Phase 8 — Adaptation
- Track player “strategy usage” stats
- Weighted counter selection
- UI messaging + preview

## Phase 9 — Content pass
- Fill MVP roster (10 enemies, 12 modules, 20 gene cards)
- Balance passes with logging

## Phase 10 — Polish
- Tutorials / tips
- SFX/VFX readability pass
- Accessibility pass (colorblind, scaling, keybinds)
