# Battle 001 — Proof of Concept Specification

> The test is simple: if watching rectangles shoot dots at other rectangles is entertaining, you've got something. If it isn't, adding acid, zombies, limbs, and beautiful graphics won't fix it.

---

## Objective

Build the minimum viable tactical combat scenario to validate the core gameplay loop:

**Prepare → Order → Fight → Analyze → Retry**

---

## Scope — What We Build

### Map
One rectangular compound. Approximately RimWorld screen-sized.

```
╔════════════════════════════════════╗
║                                    ║
║           EAST FIELD               ║
║                                    ║
║──────────── fence ─────────────────║
║                                    ║
║   building         courtyard       ║
║     ████                           ║
║     ████           RELAY           ║
║                      ◎             ║
║                                    ║
╚════════════════════════════════════╝
```

Mission: **Hold the relay for 8 minutes.**

### Defenders (6 units)

| Unit | Weapon | Role |
|------|--------|------|
| Rifleman A | Assault rifle | Versatile defender |
| Rifleman B | Assault rifle | Versatile defender |
| Rifleman C | Assault rifle | Versatile defender |
| Machine Gunner | LMG | Suppression / area denial |
| Shotgunner | Shotgun | Close quarters / breach defense |
| Medic | Pistol + medkit | Healing / support |

### Attackers (25–40 units)

Three archetypes:

| Type | Behavior | Count |
|------|----------|-------|
| Rusher | Fast, melee-focused, charges positions | 10–15 |
| Rifleman | Uses cover, shoots from range | 10–18 |
| Breacher | Targets doors/walls, explosive charges | 5–7 |

### Deployables (5 types)

| Item | Function | Limit |
|------|----------|-------|
| Wall segment | Full hard cover, blocks LOS and movement | 20 |
| Sandbag | Partial cover, shootable over | 15 |
| Barbed wire | Slows enemy movement, minor damage | 10 |
| Land mine | Explodes on contact, one-use | 6 |
| Ammo box | Resupply point for nearby units | 3 |

---

## Scope — What We Do NOT Build

- No campaign / mission select
- No research tree
- No character relationships
- No crafting
- No detailed injury model (HP only)
- No fire / gas / electricity simulation
- No sound propagation
- No weather
- No vehicles
- No multiplayer
- No fancy graphics (colored rectangles are fine)
- No persistent roster between sessions

---

## Combat Systems (POC Only)

### 1. Line of Sight + Cover
- Raycast from unit to target
- Walls block LOS completely
- Sandbags provide partial cover (e.g., 50% damage reduction)
- Flanking (attacking from outside cover arc) negates cover
- Units behind cover gain accuracy bonus

### 2. Suppression
- Each incoming round near a unit adds suppression points
- Suppression thresholds:
  - **Light (0–30%):** Slight accuracy penalty
  - **Medium (30–60%):** Significant accuracy penalty, unit crouches
  - **Heavy (60–90%):** Unit seeks nearest cover, very low accuracy
  - **Pinned (90–100%):** Unit hunkers, cannot fire, may panic
- Suppression decays at ~5% per second without incoming fire
- MG generates significantly more suppression than rifles

### 3. Damage
- Each unit has HP (e.g., 100)
- Damage = weapon base damage × cover modifier × accuracy roll
- At 0 HP: incapacitated (can be rescued by medic)
- Medic can stabilize and slowly heal downed allies

### 4. Enemy Morale (Stretch goal for POC)
- Squad-level morale value
- Decreases when: allies die nearby, suppressed, commander killed
- At low morale: enemies retreat, take worse cover, fire wildly
- At broken morale: full rout

---

## Command Palette (POC)

| Command | Key | Description |
|---------|-----|-------------|
| Move | Right-click | Move to position |
| Attack / Focus | Right-click enemy | Engage specific target |
| Watch Sector | W + drag | Define firing arc |
| Suppress Area | F + click area | Lay suppressive fire on area |
| Fallback | R + click | Set fallback position |
| Pause | Space | Pause simulation |
| Slow motion | , (comma) | Half speed |
| Normal speed | . (period) | Normal speed |
| Fast forward | / (slash) | 2× speed |

Plus standard RTS selection (box select, Ctrl+groups, etc.)

---

## Scenario Permutations

Battle 001 should have small random variations to enable replayability:

### Enemy Composition Variants
- **A — Infantry Heavy:** More riflemen, fewer breachers
- **B — Breacher Heavy:** More breachers with explosives
- **C — Rush Heavy:** More rushers, faster assault timing

### Approach Variants
- **East:** Primary approach through east field
- **North + East:** Split attack from two directions  
- **Surround:** Enemies approach from three sides (hardest)

Combination is randomly selected (or player-chosen for testing).

---

## Victory / Defeat Conditions

**Victory:** Relay survives 8 minutes OR all enemies eliminated/routed.

**Defeat:** Relay destroyed OR all defenders incapacitated.

---

## The Core Test

Build this:

```
              RAIDERS
                 ↓

       ###################
       #                 #
       #       WIRE      #
       #      //////     #
       #                 #
       #  MG →→→→→→→→    #
       #        □ □      #
       #    R       R    #
       #                 #
       ###### DOOR #######
```

Tell the MG: Cover this lane. Suppress groups.
Tell the rifles: Protect the MG's flanks.
Tell shotgunner: Stay behind the door. Engage if breached.

Press **START RAID**.

Watch.

**If watching that play out is entertaining — even with rectangles shooting dots — you've got something.**
