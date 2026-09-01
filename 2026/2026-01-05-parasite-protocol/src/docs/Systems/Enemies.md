# System — Enemies (AI, Pathing, Families, Spawning, Bosses)

Date: 2026-01-05

This doc specifies enemy behavior and the recommended pathing approach for a Bevy 2D arena.

---

## 1) Design goals for enemy behavior
- Enemies should be **readable**: players can predict threats.
- Enemies should be **cheap to simulate**: avoid per-enemy A*.
- Enemies should pressure **different systems**: membrane, shipping, circuits, infection.

---

## 2) Movement & pathfinding approach (recommended)
### Hybrid: Flow field + local steering
**Why:** you have many units and a mostly-open arena with a few static obstacles (organelles).

#### Global navigation
- Precompute a **distance field** (or flow field) toward target(s):
  - Targets: breach openings, nucleus, mitochondria, ER/Golgi (depending on enemy role)
- Represent arena as a grid (e.g., 128×128).
- Compute cost grid considering static obstacles (organelles).
- Update flow field:
  - On map start
  - When new high-level target changes (e.g., breach opens)
  - Low frequency (e.g., every 0.5–1.0 sec) if needed

#### Local steering
Per enemy per tick:
- Follow the flow vector from the field
- Add separation (avoid clumping too hard)
- Add obstacle avoidance (simple circle avoidance around organelles)
- Optional: mild randomness for organic movement

This gives “swarm behavior” with minimal CPU cost.

### Alternative (if you need exact paths)
- Use A* only for **bosses** or rare units, and cache results.
- Vesicle routing should use track graph shortest-path (separate from enemies).

---

## 3) Enemy AI behaviors (state machines)
Each enemy uses a small state machine:

Common states:
- **Approach** (move toward target)
- **Engage** (attack membrane/module/organelles)
- **Special** (spawn node, hijack, corrupt)
- **Flee/Retreat** (rare; for certain types)
- **Die**

**AI decision rules must be data-driven** where possible:
- target priority list
- trigger conditions for special ability
- cooldown timers

---

## 4) Enemy families & roles (MVP set)
### Virus family
- **Role:** fast swarm; pressures sensors and circuit throughput
- **Traits:** small hitbox, high speed, low HP
- **Specials (examples):**
  - Hijack manufacturing: disables 1 ribosome slot briefly if reaches ER/Golgi zone
  - Integration attempt (elite): heads for nucleus with a channel-time

### Bacteria family
- **Role:** armored brute; pressures raw DPS and membrane durability
- **Traits:** slower, higher HP/armor
- **Specials:**
  - Toxin puddles: create localized “shipping slow” + mild stress gain zone

### Spore/Fungal family
- **Role:** spreader; pressures containment layer
- **Traits:** medium speed, medium HP
- **Specials:**
  - Drops infection nodes on death or periodically
  - Grows biofilm-like patches (terrain debuff)

### Disruptor (cross-family subtype)
- **Role:** attacks circuits/logistics rather than HP
- **Specials:**
  - “Signal noise” aura: increases trigger costs or adds misfire chance
  - “Cut tracks” attack: damages track segments in melee range

---

## 5) Spawn mechanics & timing
### Wave-based spawner (threat budget)
- Each wave has a **budget**.
- Each enemy type has a point cost.
- Spawner emits enemies in **packets** with short gaps:
  - packet size 3–20 depending on enemy family
  - gaps 0.5–2.0 sec

**Spawn sources**
- Primary: membrane breach openings
- Secondary: “micro-tears” events (temporary spawners) for later waves

**Spawn rules**
- Early waves: 1–2 openings max
- Mid waves: 2–4 openings
- Late: 4+ openings, but avoid overwhelming the UI

### Breach binding (virus flavor)
Some enemies “bind” to the membrane before spawning inside:
- They travel to edge, channel for `bind_time`,
- If not interrupted, they create a breach opening.

---

## 6) Boss behaviors (spec examples)
Bosses should have **phases** and should telegraph.

### Boss A: Retrovirus Integrator
- **Target:** nucleus
- **Phase 1:** attaches to membrane and creates a long-lived breach
- **Phase 2:** moves inward; periodically spawns virion swarms
- **Phase 3 (integration):** channels at nucleus for 8–12 sec
  - If completes: permanent debuff for rest of run (or immediate loss in hard mode)
- **Counterplay:** interrupt channel (tag+execute, burst damage, or specific “interferon” gene)

### Boss B: Biofilm Builder (bacterial)
- **Phase 1:** slow advance; leaves biofilm patches behind
- **Phase 2:** summons armored adds inside biofilm zones
- **Phase 3:** “fortify” — huge armor until biofilm nodes destroyed
- **Counterplay:** cleanse nodes, then burst

### Boss C: Spore Bloom
- **Phase 1:** spreads infection aggressively
- **Phase 2:** creates multiple infection nodes that pulse
- **Phase 3:** “bloom” — massive infection surge unless nodes cleared
- **Counterplay:** prioritize containment; use mobile cleaners

---

## 7) Telemetry inputs (for adaptation system)
Record per wave:
- damage sources (AoE vs single vs execute)
- CC sources (slow, snare)
- infection cleanse frequency
- average TTK (time to kill) per family
- shipping stall time

---

## Definition of Done
- [ ] Enemies follow flow field + steering without per-unit pathfinding spikes.
- [ ] At least 3 families have distinct roles and counters.
- [ ] Spawner can emit packeted waves from breach openings.
- [ ] At least 1 boss has multi-phase behavior with clear telegraphs.
- [ ] Enemy traits and abilities are data-driven.
