# Content_Authoring_Guide

## Goals
- Keep content modular and combinable.
- Avoid creating “must pick” modules by giving each clear counters and costs.

## Adding a new enemy (checklist)
1. Pick family: virus/bacteria/spore/toxin/prion
2. Decide role: swarm/brute/support/disruptor/boss
3. Define how it pressures the player:
   - manufacturing disruption?
   - shipping disruption?
   - infection spread?
   - circuit noise?
4. Define clear counters (at least 2).
5. Add UI icons: family + key trait (stealth, armor, spreader, etc.)
6. Test in 3 waves with different builds.

## Adding a new module
### Receptor
- Must be readable: what event triggers it?
- Must have at least one filter option (family or tag)
- Must "explain itself" in Circuit View

### Relay
- Must enable at least 2 distinct combos
- Must have an obvious drawback (ATP cost, delay, reduced output)

### Effector
- Must specify:
  - target rules (closest/strongest/tagged)
  - effect radius and duration
  - side effect (stress, ATP spike, self-damage)

## Adding a gene card
- Each card should create a tradeoff, not pure power.
- Prefer rules changes over raw stat boosts.

## Common pitfalls
- Too many overlapping AoE circles = unreadable.
- Triggers spamming (gate/threshold is your friend).
- Infection either irrelevant or instantly fatal—tune spread rates carefully.
