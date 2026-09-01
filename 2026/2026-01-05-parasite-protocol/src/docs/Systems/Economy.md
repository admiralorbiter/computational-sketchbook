# System — Economy (ATP / Blocks / Stress / Membrane Integrity)

Date: 2026-01-05

This doc defines concrete mechanics and baseline numbers for the economy. Treat values as *starting points*; tune after playtests.

---

## 1) Resources overview
### Primary
- **ATP**: spendable energy used to (a) manufacture modules, (b) trigger circuits, (c) activate abilities, (d) repair.
- **Blocks**: building materials used to queue modules and tracks.
  - MVP recommendation: one unified currency **Biomass** to keep pacing simple.
  - Optional advanced: three pools (**Amino Acids**, **Lipids**, **Nucleotides**) with different sinks.

### Control meters
- **Stress (0–100)**: rises from high-power responses; causes penalties.
- **Membrane Integrity**: local and global measure affecting breach rate and durability.

---

## 2) ATP generation model
### Local generation (mitochondria)
Each mitochondrion provides ATP in a radius:
- `ATP_gen_total = Σ (mito_output * mito_efficiency * coverage_factor)`
- `coverage_factor` can be 1.0 globally (simpler) or distance-weighted (more strategic).

**Baseline MVP numbers (start here):**
- Each mitochondrion output: **+8 ATP/sec**
- Typical map: **2 mitochondria** → ~16 ATP/sec baseline
- ATP storage cap: **200 ATP** (upgradeable)

### Distance / locality (recommended, not required for MVP)
If you want locality:
- Compute ATP availability per region via “power radius” zones.
- Modules outside a power zone pay a surcharge or have reduced trigger capacity.

Simpler compromise:
- Keep global ATP, but add **“power boost”** for modules within radius:
  - `trigger_cost *= 0.85` if powered
  - `shipping_speed *= 1.15` if routes pass near mitochondria

---

## 3) ATP consumption
### Spend categories
1. **Manufacturing costs**
   - On queue: pay blocks + partial ATP (commitment)
   - On completion: pay remaining ATP (or pay all upfront for simplicity)
2. **Trigger costs (runtime)**
   - Per activation of effectors / relays (amplify costs extra)
3. **Abilities**
   - Large one-time ATP drain + stress
4. **Repairs / cleanse**
   - Cost ATP + blocks depending on action

**Baseline costs (MVP)**
- Receptor: 10 ATP + 8 biomass, trigger cost 0–1 ATP
- Relay: 15 ATP + 10 biomass, trigger cost 1–2 ATP
- Effector: 25 ATP + 15 biomass, trigger cost 3–6 ATP
- Actin track segment: 2 ATP + 2 biomass
- Microtubule segment: 5 ATP + 4 biomass
- Cleanse (small area): 20 ATP
- Emergency membrane patch: 30 ATP

**Suggested rule:** Never let “trigger costs” exceed generation so much that the player is forced into downtime; instead, force tradeoffs via stress and opportunity cost.

---

## 4) Blocks (Biomass) mechanics
### Acquisition
- Passive: +2 biomass/sec baseline (optional)
- Wave reward: `biomass += wave_budget * 0.8` (tunable)
- Recycling (autophagy): reclaim 50–80% of module biomass cost

### Sinks
- Queueing modules and tracks
- Repairs and cleanse options between waves

**MVP suggestion:** Most biomass comes from wave rewards + recycling, not passive.

---

## 5) Stress system
Stress represents self-damage / instability from overclocking defenses.

### Stress gain sources (baseline)
- ROS-style AoE effector trigger: +3–6 stress
- Amplify relay trigger: +1 stress per use
- Emergency abilities: +10–25 stress
- Running ATP below 10% cap for >5 sec: +1 stress/sec (panic metabolism)

### Stress decay
- Base decay: **-2 stress/sec** during Recovery
- Combat decay: **-0.5 stress/sec** (slow)
- Optional: Decay increased by “homeostasis” upgrades

### Thresholds and consequences
- **0–24**: Stable (no penalties)
- **25–49**: Mild stress
  - +10% manufacturing time
  - +10% infection spread rate (cell vulnerable)
- **50–74**: Severe stress
  - +25% manufacturing time
  - +20% trigger costs
  - 5% chance on trigger: “misfire” (cooldown doubled) — show UI warning
- **75–99**: Critical stress
  - +40% manufacturing time
  - +35% trigger costs
  - 10% chance: temporary module disable (2–4 sec)
- **100**: Collapse event
  - Either immediate loss OR force **Apoptosis Protocol** decision:
    - wipe enemies + reduce infection by 50%
    - lose 1 life / apply permanent debuff / end run depending on your structure

**Design note:** The player should feel stress as an escalating “you can still clutch it, but it’s dangerous” meter.

---

## 6) Membrane Integrity system
### Representation
- Membrane split into **N segments** around the ring (e.g., N=24 or 32).
- Each segment has:
  - `segment_hp`
  - `weakspot_modifier` (some segments are “raft weak”)

### Breach chance & pressure
A segment’s breach attempt rate:
- `breach_rate = base_rate * weakspot_modifier * (1 + wave_pressure) * (1 + infection_edge_factor)`
- `durability_factor = clamp(0.25, 1.0, segment_hp / segment_hp_max)`
- Final chance can be:
  - `final_breach_rate = breach_rate * (1.1 - durability_factor)`

**Baseline MVP numbers**
- Segment HP max: 100
- Base breach attempt rate per segment: 0.02/sec (tunable)
- Weakspot modifier: 1.3 on 3–6 segments, else 1.0
- When a breach occurs: segment HP -15; spawn a “breach opening” for X seconds

### Repairs
- Repair action targets a segment or small arc:
  - +25 HP for 20 ATP + 10 biomass
- Some gene cards improve repair efficiency.

---

## 7) Balancing formulas & knobs (summary)
- ATP generation: mito count, output, storage cap
- Module costs: upfront vs per-trigger
- Stress curve: gain values and threshold penalties
- Membrane: segment count, base breach rate, HP max, repair rate
- Biomass: wave reward multiplier, recycle %

---

## Definition of Done
- [ ] ATP generation is stable and visible in UI (+/sec).
- [ ] Every module and ability has defined ATP + stress costs.
- [ ] Stress thresholds create clear gameplay changes with warnings.
- [ ] Membrane segments track HP and influence breach rates.
- [ ] A run can be balanced by adjusting the knobs in this doc.
