# System — Tracks (Microtubules vs Actin, Placement, Routing, Repair, Enemy Interaction)

Date: 2026-01-05

Tracks form the game’s logistics backbone: they speed module delivery and create strategic routing choices.

---

## 1) Track types and differences
### Microtubules (highways)
- **Purpose:** long-range fast shipping
- **Cost:** higher
- **Properties (baseline)**
  - Vesicle speed multiplier: **×2.0**
  - Capacity: high (less congestion penalty)
  - Placement: longer segments, straighter preferred (optional rule)
  - Vulnerability: moderate to “cut track” enemies

### Actin (local mesh)
- **Purpose:** local routing + minor enemy control
- **Cost:** low
- **Properties (baseline)**
  - Vesicle speed multiplier: **×1.3**
  - Capacity: low-medium (congestion more likely)
  - Bonus: slows enemies in a small radius (e.g., -10% speed) *if you choose*
  - Vulnerability: higher to infection “gunk”

---

## 2) Track placement rules
### Common
- Placement uses a “paint” tool along the grid.
- Tracks occupy edges between grid cells (graph edges).
- Tracks can overlap visually but should be stored as:
  - a graph with edge type (microtubule/actin)

### Connection rules
- Tracks can connect to:
  - ER/Golgi hub (origin)
  - Module placement points (destination snap)
  - Mitochondria (optional: “powered corridor”)
- Allow freeform placement anywhere inside membrane, but prevent placement through organelles.

### Optional constraints (add later if desired)
- Microtubules prefer straighter lines (turn penalties).
- Actin cannot exceed a max density per area (crowding rule).

---

## 3) Vesicle routing algorithm (shipping)
### Represent tracks as a weighted graph
- Nodes: grid intersections or cell centers
- Edges: track segments with weights

#### Edge weights
- Base distance weight: 1.0 per segment
- Speed modifier converts to effective cost:
  - `effective_cost = base_cost / speed_multiplier`
- Congestion adds penalty:
  - `effective_cost *= (1 + congestion_factor)`

### Path selection
On shipment creation:
1. Find nearest graph node to origin (ER/Golgi) and destination (placement point).
2. Run shortest path (Dijkstra) on track graph.
3. If no path exists:
   - Fall back to “free travel” at slow speed (or disallow placement if you want harsher rules).

### Congestion model (cheap)
Maintain per-edge `load`:
- Increment when vesicle enters edge, decrement when leaves.
- `congestion_factor = load / capacity`
  - capacity: higher for microtubules

Update edge loads in a resource each tick.

---

## 4) Track repair mechanics
Tracks degrade or become impaired via:
- Infection intensity over threshold
- Enemy “cut track” attacks (direct damage)

### Track health
Each edge has:
- `hp`, `hp_max`
- `gunk_level` (from infection)

Effects:
- Low hp reduces speed multiplier
- High gunk reduces speed multiplier and increases stall chance

### Repairs
- Manual repair tool:
  - targets a segment or small brush
  - costs ATP + biomass
  - reduces gunk, restores hp
- Recovery option can repair a larger section at discount.

Baseline numbers:
- Repair 5 segments: 15 ATP + 10 biomass
- Clean gunk on 5 segments: 10 ATP + 5 biomass

---

## 5) Enemy interactions with tracks
Recommended interactions (pick 1–2 for MVP):
1. **Actin slow aura:** enemies moving through actin mesh are slowed slightly.
2. **Track cutting:** disruptor enemies damage track edges on contact.
3. **Track avoidance/adaptation:** some evolved enemies ignore slow effects or tunnel.

Important: do NOT let enemies path “perfectly” along tracks unless you want that dynamic; tracks primarily serve shipping, with optional soft CC.

---

## Definition of Done
- [ ] Player can place both track types.
- [ ] Vesicles route using shortest path on the track graph.
- [ ] Congestion affects route cost or speed (even simple).
- [ ] Infection or enemies can impair track performance.
- [ ] Player can repair tracks via tool or recovery option.
