# Combat Math Specification

> All values are starting points for tuning. The fixed-tick simulation (20 ticks/sec)
> and data-driven architecture mean every number here lives in a data file and can
> be changed without touching code.

---

## Design Targets

| Parameter | Target | Rationale |
|-----------|--------|-----------|
| Battle duration | ~8 minutes (480s) | Long enough for plans to unfold, short enough to replay |
| Sim tick rate | 20 ticks/sec | 50ms per tick; smooth enough for real-time, cheap enough for mass sim |
| Defenders | 6 | Small enough to care about each one |
| Attackers | 25–40 | ~5:1 to 7:1 ratio; defenders need force multiplier from prep |
| TTK (exposed, accurate) | 3–6 seconds | Fast enough to punish mistakes, slow enough for reaction |
| TTK (behind cover) | 10–20 seconds | Cover must feel essential |
| TTK (suppressed + cover) | 25–40+ seconds | Suppressed defenders survive but can't fight back effectively |
| Defender win rate (good play) | ~65% | Should feel hard but fair |
| MG suppression saturation | ~3 seconds of fire | MG should lock down a lane quickly |

---

## 1. Damage Formula

```
HitChance = BaseAccuracy × CoverMod × SuppressionMod × RangeMod × MovementMod
Damage    = WeaponDamage × ArmorMod    (if hit)
```

### Hit Resolution (per shot)

1. Roll `rand(0.0, 1.0)`
2. If roll ≤ HitChance → **HIT** → apply damage
3. If roll ≤ HitChance + 0.3 → **NEAR MISS** → apply suppression to target
4. If roll > HitChance + 0.3 → **WIDE MISS** → no effect

Near misses generating suppression is critical — it means an inaccurate weapon
(like the MG at range) still has tactical value even when it's not hitting.

---

## 2. Weapon Data

### Design Philosophy

Each weapon should have a **clear tactical role** that emerges from its stats,
not from a special ability bolted on.

- **Rifle:** Reliable, accurate, moderate everything. The baseline.
- **LMG:** Poor accuracy but extreme fire rate → massive suppression, occasional kills.
- **Shotgun:** Devastating damage at close range, useless beyond ~8 tiles.
- **Pistol (medic):** Weak but functional self-defense.

### Weapon Stats Table

| Stat | Assault Rifle | LMG | Shotgun | Pistol |
|------|:---:|:---:|:---:|:---:|
| **Damage per hit** | 18 | 12 | 35 | 10 |
| **RPM** | 120 | 600 | 40 | 90 |
| **Shots per tick** (at 20 tps) | 0.10 | 0.50 | 0.033 | 0.075 |
| **Seconds between shots** | 0.50 | 0.10 | 1.50 | 0.67 |
| **Base accuracy** | 0.70 | 0.35 | 0.85* | 0.50 |
| **Accuracy (moving)** | 0.35 | 0.10 | 0.60 | 0.35 |
| **Effective range (tiles)** | 30 | 35 | 6 | 15 |
| **Max range (tiles)** | 45 | 50 | 10 | 25 |
| **Suppression per round** | 3 | 5 | 8 | 1 |
| **Magazine size** | 30 | 100 | 8 | 15 |
| **Reload time (sec)** | 2.0 | 5.0 | 3.5 | 1.5 |
| **Setup time (sec)** | 0 | 1.5 | 0 | 0 |

*Shotgun accuracy has a steep range falloff (see below).

### RPM → Shots Per Tick

At 20 ticks per second:
```
shots_per_tick = RPM / 60 / 20
```
When `shots_per_tick < 1.0`, accumulate fractionally each tick and fire when ≥ 1.0.

### Range Modifier

```
if distance ≤ effective_range:
    range_mod = 1.0
elif distance ≤ max_range:
    range_mod = 1.0 - ((distance - effective_range) / (max_range - effective_range)) × 0.8
else:
    range_mod = 0.0   # can't engage
```

This means at max range, accuracy drops to 20% of base. Beyond max range, can't fire.

### Shotgun Range Curve (Special)

Shotgun uses a steeper falloff — devastation up close, useless far:
```
if distance ≤ 3:
    range_mod = 1.2    # bonus at point blank
elif distance ≤ effective_range:
    range_mod = 1.0
elif distance ≤ max_range:
    range_mod = 1.0 - ((distance - effective_range) / (max_range - effective_range)) × 0.95
else:
    range_mod = 0.0
```

---

## 3. TTK Validation

### Scenario: Rifleman vs Exposed Target at Medium Range (20 tiles)

```
HitChance = 0.70 (base) × 1.0 (no cover) × 1.0 (no suppression) × 1.0 (in range) = 0.70
DPS = (120 RPM / 60) × 0.70 × 18 damage = 25.2 effective DPS
TTK = 100 HP / 25.2 = ~4.0 seconds ✓  (target: 3–6s)
```

### Scenario: Rifleman vs Target Behind Sandbag

```
HitChance = 0.70 × 0.50 (sandbag) × 1.0 × 1.0 = 0.35
DPS = 2.0 × 0.35 × 18 = 12.6 effective DPS
TTK = 100 / 12.6 = ~7.9 seconds
```

With some incoming suppression (0.75 mod):
```
HitChance = 0.70 × 0.50 × 0.75 = 0.26
DPS = 2.0 × 0.26 × 18 = 9.4
TTK = 100 / 9.4 = ~10.6 seconds ✓  (target: 10–20s)
```

### Scenario: MG vs Exposed Target at 25 tiles

```
HitChance = 0.35 × 1.0 × 1.0 × 1.0 = 0.35
DPS = (600/60) × 0.35 × 12 = 42.0 effective DPS
TTK = 100 / 42.0 = ~2.4 seconds
```

MG **can** kill exposed targets quickly — but that's intentional.
The point is that being exposed in an MG's firing arc should be lethal.

### Scenario: MG vs Target Behind Sandbag

```
HitChance = 0.35 × 0.50 = 0.175
DPS = 10.0 × 0.175 × 12 = 21.0
TTK = 100 / 21.0 = ~4.8 seconds
```

But the suppression output matters more than the kills here.

### Scenario: Shotgun at 2 Tiles (Breach!)

```
HitChance = 0.85 × 1.2 (point blank) = 1.0 (capped)
DPS = (40/60) × 1.0 × 35 = 23.3 effective DPS
TTK = 100 / 23.3 = ~4.3 seconds
```

Two shots, ~3 seconds. Very nasty in a doorway. Exactly right.

### Scenario: Shotgun at 9 Tiles (Too Far)

```
range_mod = 1.0 - ((9-6)/(10-6)) × 0.95 = 0.29
HitChance = 0.85 × 0.29 = 0.25
DPS = 0.67 × 0.25 × 35 = 5.8
TTK = 100 / 5.8 = ~17.2 seconds
```

Basically useless at range. Correct.

---

## 4. Cover System

### Cover Values

| Cover Type | Damage Reduction | Accuracy vs. Target | Blocks LOS |
|------------|:---:|:---:|:---:|
| None / exposed | 0% | ×1.0 | No |
| Soft cover (furniture, thin wood) | 20% | ×0.80 | No |
| Sandbag | 40% | ×0.50 | No |
| Hard cover (wall edge, concrete) | 60% | ×0.35 | Partial |
| Full wall | 100% | N/A | Yes |

### How Cover Is Determined

Cover is **directional**. A sandbag only protects you from fire coming from the
direction the sandbag faces.

```
cover_value = 0.0  (default: exposed)

For each obstacle between shooter and target:
    if obstacle blocks LOS completely:
        can't engage (full wall)
    if obstacle provides cover:
        cover_value = max(cover_value, obstacle.cover_rating)

# Flanking check
angle = angle_between(shooter_position, target_position, cover_facing)
if angle > 90°:
    cover_value = 0.0   # flanked — cover doesn't help
```

### CoverMod (used in hit chance)

```
CoverMod = 1.0 - (cover_value × 0.7)
```

So a sandbag (0.40 cover) gives:
```
CoverMod = 1.0 - (0.40 × 0.7) = 0.72
```

Wait, let me reconcile this. I want sandbag to give approximately ×0.50 hit chance.

Let me simplify — the cover table's "Accuracy vs. Target" column IS the CoverMod:

```
CoverMod = cover_accuracy_modifier   # directly from the table above
```

And damage that does hit is further reduced:
```
FinalDamage = WeaponDamage × (1.0 - cover_damage_reduction)
```

So a sandbag:
- Reduces hit chance to ×0.50
- Hits that land deal ×0.60 damage

Combined survivability multiplier:
```
effective_survivability = 1.0 / (0.50 × 0.60) = 3.33×
```

For hard cover:
```
effective_survivability = 1.0 / (0.35 × 0.40) = 7.14×
```

That feels right — hard cover should be extremely strong but also extremely
limiting (you can't shoot through it easily either).

### Leaning / Peeking

A unit behind a wall can "peek" to fire, briefly exposing themselves:
- While peeking: treated as soft cover (×0.80 hit chance against them)
- While not peeking: full wall, can't be hit, can't fire
- Peeking happens automatically when the unit wants to shoot

---

## 5. Suppression System

### Design Goal

Suppression should be **the primary tactical tool**, not just a status effect.
An MG should be able to lock down an avenue of approach even if it rarely kills anyone.

### Suppression Points

Each unit has a `suppression` value: 0–100.

```
suppression += incoming_suppression_value   # per round fired near them
suppression -= decay_rate × delta_time      # per second without incoming fire
suppression = clamp(suppression, 0, 100)
```

### Suppression Sources

Suppression comes from:
- **Hits:** Full suppression value of the weapon
- **Near misses:** 70% of weapon's suppression value
- **Wide misses:** 0 suppression
- **Explosions nearby:** 30 suppression (flat)
- **Ally killed within 5 tiles:** 15 suppression (flat)

### Suppression Thresholds & Effects

| Level | Range | Accuracy Modifier | Behavior |
|-------|:-----:|:-----------------:|----------|
| **Clear** | 0–20 | ×1.00 | Normal behavior |
| **Light** | 21–40 | ×0.85 | Slight flinch; unit crouches more |
| **Medium** | 41–60 | ×0.60 | Seeks cover if not in it; reduced fire rate |
| **Heavy** | 61–80 | ×0.30 | Must be in cover to fire; very inaccurate |
| **Pinned** | 81–100 | ×0.05 | Cannot fire; hunkers down; may panic-crawl |

### SuppressionMod (used in hit chance)

```
if suppression <= 20: return 1.00
if suppression <= 40: return 0.85
if suppression <= 60: return 0.60
if suppression <= 80: return 0.30
return 0.05
```

Or as a smooth curve:
```
SuppressionMod = max(0.05, 1.0 - (suppression / 100.0) × 0.95)
```

I'd recommend the **threshold version** for the prototype — it's more legible to the
player ("he's PINNED" is clearer than "his accuracy is at 23.7%").

### Suppression Decay

```
decay_rate = 12.0 points per second   # (when no incoming fire)
```

So a pinned unit (100 suppression) takes ~8.3 seconds to fully recover.
A lightly suppressed unit (30) recovers in ~2.5 seconds.

### MG Suppression Output

The MG fires at 600 RPM = 10 rounds/second.

Each round that's a near miss or hit applies 5 suppression.

At a typical hit rate + near miss rate against an exposed target:
```
hit_chance = 0.35
near_miss_chance = 0.30  (rolls between 0.35 and 0.65)

suppression_per_second = 10 × (0.35 × 5.0 + 0.30 × 3.5) = 10 × (1.75 + 1.05) = 28.0/sec
```

Time to pin an exposed target: ~3.5 seconds. ✓

Against a target behind sandbag:
```
hit_chance = 0.175
near_miss_chance = 0.30

suppression_per_second = 10 × (0.175 × 5.0 + 0.30 × 3.5) = 10 × (0.875 + 1.05) = 19.25/sec
```

Time to pin behind sandbag: ~5.2 seconds. Still effective. ✓

### Rifle Suppression Output

Rifle fires at 120 RPM = 2 rounds/second, 3 suppression per round.

```
suppression_per_second = 2 × (0.70 × 3.0 + 0.30 × 2.1) = 2 × (2.1 + 0.63) = 5.46/sec
```

One rifleman can barely keep someone suppressed (5.46 vs 8.0 decay).
Three riflemen can keep someone moderately suppressed. That's correct — rifles
should need concentration of fire for suppression.

---

## 6. Movement

### Movement Speeds

| State | Speed (tiles/sec) |
|-------|:---:|
| Sprint | 6.0 |
| Normal move | 4.0 |
| Crouched / careful | 2.0 |
| Crawl (pinned) | 0.5 |
| Setup/teardown MG | 0 (stationary for 1.5s) |

### Movement Modifier on Accuracy

| State | MovementMod |
|-------|:---:|
| Stationary | ×1.0 |
| Crouched move | ×0.7 |
| Normal move | ×0.5 |
| Sprint | ×0.15 |

### Terrain Movement Modifiers

| Terrain | Speed Multiplier |
|---------|:---:|
| Open ground | ×1.0 |
| Rough terrain | ×0.7 |
| Barbed wire | ×0.3 |
| Through door | ×0.6 (brief pause) |

---

## 7. Unit Data

### Defenders

| Unit | HP | Speed | Weapon | Special |
|------|:---:|:---:|--------|---------|
| Rifleman A | 100 | 4.0 | Assault Rifle | — |
| Rifleman B | 100 | 4.0 | Assault Rifle | — |
| Rifleman C | 100 | 4.0 | Assault Rifle | — |
| Machine Gunner | 110 | 3.5 | LMG | Setup/teardown time; slower |
| Shotgunner | 100 | 4.0 | Shotgun | — |
| Medic | 80 | 4.5 | Pistol | Can heal; faster |

### Medic Healing

```
heal_rate = 5 HP/sec   (while adjacent to wounded ally, not in combat)
stabilize_time = 3.0 seconds  (stops bleeding / prevents death)
```

A downed ally (0 HP) bleeds out in 30 seconds without stabilization.

### Attackers

| Unit | HP | Speed | Weapon | Morale | Special |
|------|:---:|:---:|--------|:---:|---------|
| Rusher | 70 | 5.5 | Melee (knife) | 40 | Fast; 25 damage per attack, 1.5s cooldown |
| Enemy Rifleman | 90 | 4.0 | Assault Rifle | 60 | Uses cover; fights like defenders |
| Breacher | 120 | 3.5 | Shotgun + charges | 70 | Can breach walls; tanky |

### Melee Combat

When a rusher reaches an adjacent tile:
```
melee_damage = 25
melee_cooldown = 1.5 seconds
melee_hit_chance = 0.80

effective_melee_DPS = 25 × 0.80 / 1.5 = 13.3
TTK vs defender = 100 / 13.3 = ~7.5 seconds
```

A single rusher is manageable. Five rushers in melee is catastrophic.
That's the right dynamic — they're individually weak but lethal en masse.

### Breach Charges

```
breach_damage = 200  (vs. structures only)
placement_time = 3.0 seconds (breacher is vulnerable)
detonation_delay = 2.0 seconds (beeping, gives defender warning)
blast_radius = 2 tiles
blast_damage_to_units = 60
```

A wall has 150 HP, so one charge destroys it plus damages nearby units.

---

## 8. Deployable Data

### Build Budget

For Battle 001, the player gets **200 build points** to spend.

| Deployable | Cost | HP | Cover Value | Blocks LOS | Blocks Movement | Special |
|------------|:---:|:---:|:---:|:---:|:---:|---------|
| Wall segment | 15 | 150 | Full (1.0) | Yes | Yes | Can be breached |
| Sandbag | 8 | 60 | 0.40 | No | No | Shootable over |
| Barbed wire | 5 | 30 | 0 | No | Slows (×0.3) | 2 damage/sec to units crossing |
| Land mine | 12 | — | 0 | No | No | 80 damage in 2-tile radius; one use; hidden |
| Ammo box | 10 | 40 | 0 | No | No | Units within 3 tiles reload 50% faster |

### Budget Validation

With 200 points, example builds:
- **Fortress:** 8 walls (120) + 5 sandbags (40) + 4 mines (48) = 208 → tight, forces tradeoffs ✓
- **Wire + mines:** 10 wire (50) + 6 mines (72) + 5 sandbags (40) + 2 walls (30) = 192 ✓
- **Minimal:** 10 sandbags (80) + 6 mines (72) + 4 wire (20) = 172 → saves nothing, balanced ✓

Budget should create interesting choices, not allow everything. ✓

---

## 9. Enemy Morale System

### Squad-Level Morale

Each enemy squad has a shared `morale` value (starting at their base morale).

```
morale_events:
    ally_killed_nearby (5 tiles):     -8
    ally_killed_same_squad:           -12
    squad_leader_killed:              -25
    suppressed (per second):          -2
    pinned (per second):              -5
    under_fire_no_cover:              -3/sec
    successful_kill:                  +10
    breach_success:                   +15
    advancing:                        +1/sec
    allies_nearby (per ally in 5t):   +0.5/sec
```

### Morale Thresholds

| Level | Value | Effect |
|-------|:---:|--------|
| **Confident** | 60–100 | Normal behavior; will advance into fire |
| **Shaken** | 40–59 | Won't advance without cover; prefers flanking |
| **Wavering** | 20–39 | Won't advance at all; defensive fire only |
| **Breaking** | 1–19 | Retreating; only fires if cornered |
| **Routed** | ≤0 | Fleeing the map; drops weapons |

### Morale Recovery

```
morale_recovery = 2.0 per second (when not under fire and in cover)
morale_recovery = 0.5 per second (when under fire but in cover)
morale_recovery = 0.0 (when under fire and exposed)
```

### How This Plays Out

An MG suppressing a squad of 5 enemy riflemen:
- ~5 seconds to pin them (suppression)
- Suppression drains morale at -5/sec while pinned
- If pinned for 12 seconds: -60 morale → squad breaks from Confident to Breaking
- They start retreating

But an MG can only cover ONE lane.

If 5 enemies attack from two directions, the MG pins one group while the other advances.
**That's the tactical problem.** ✓

---

## 10. Scenario Permutations — Battle 001

### Base Force (randomly composed)

| Variant | Rushers | Riflemen | Breachers | Total | Character |
|---------|:---:|:---:|:---:|:---:|-----------|
| A — Infantry Heavy | 8 | 18 | 4 | 30 | Hardest to suppress; lots of return fire |
| B — Breacher Heavy | 8 | 12 | 7 | 27 | Will punch through walls; must defend everywhere |
| C — Rush Heavy | 18 | 10 | 5 | 33 | Overwhelming melee wave; wire and mines crucial |

### Approach (randomly selected)

| Variant | Description | Difficulty |
|---------|-------------|:---:|
| East Only | All enemies from east field | ★★ |
| North + East | Split ~60/40 | ★★★ |
| Three Sides | Split ~40/30/30 | ★★★★ |

### Timing

Enemies arrive in 2–3 waves:
```
wave_1: 60% of force at t=0:00 (battle start)
wave_2: 30% of force at t=2:30
wave_3: 10% of force at t=5:00 (if applicable)
```

This prevents the player from facing the entire force at once while
maintaining pressure throughout the 8-minute timer.

---

## 11. Balance Simulation (Napkin Math)

### Can 6 Defenders Win Against 30 Attackers?

**Defender total DPS** (all stationary, unimpeded):
```
3 rifles:   3 × 25.2 = 75.6 DPS
1 MG:       1 × 42.0 = 42.0 DPS  (but primarily suppressing, not killing)
1 shotgun:  minimal at range
1 medic:    minimal (healing instead)

Effective killing DPS ≈ 75-80 (rifles doing most killing work)
```

**Time to eliminate 30 enemies** (if all exposed, no cover):
```
30 × 100 HP / 80 DPS = 37.5 seconds
```

Obviously unrealistic — enemies use cover and aren't all in LOS at once.

**More realistic estimate:**
```
Average engagement: 3-4 enemies visible at once
Cover reduces DPS by ~50%: 40 effective DPS
Suppression reduces by another ~20%: 32 effective DPS
But MG suppression keeps enemies from being effective

32 DPS × 480 seconds = 15,360 total damage
30 enemies × 100 avg HP = ~2,700 total enemy HP

Ratio: 15,360 / 2,700 = 5.7× overkill on paper
```

But:
- Enemies aren't always in engagement range
- Defenders take fire and get suppressed too
- Ammo runs out (rifles: 30-round mags, reload takes 2s)
- Rushers close to melee and disrupt everything
- Breachers create new attack angles

The math suggests defenders have enough raw firepower IF their positioning
is good and the MG keeps lanes locked down. Bad positioning → overrun.

**That's the game.** ✓

---

## 12. Tile / Distance Reference

One tile = roughly 1 meter for intuitive reference.

| Distance | Context |
|:---:|---------|
| 1 tile | Melee range; adjacent |
| 3 tiles | Shotgun devastating range |
| 6 tiles | Shotgun effective range limit |
| 10 tiles | Close combat; room-to-room |
| 20 tiles | Medium engagement; across courtyard |
| 30 tiles | Rifle effective range; across compound |
| 35 tiles | MG effective range |
| 45 tiles | Rifle max range |
| 50 tiles | MG max range; edge of map |

### Map Size

Battle 001 compound: approximately **60 × 40 tiles**.

At 32 pixels per tile → 1920 × 1280 pixels (fits a 1080p screen with UI).

---

## 13. Constants Summary (for data files)

### Quick Reference

```
# Simulation
TICK_RATE = 20            # ticks per second
TILE_SIZE = 32            # pixels per tile

# Combat
BASE_HP = 100
BLEEDOUT_TIME = 30.0      # seconds until downed unit dies
HEAL_RATE = 5.0           # HP per second (medic)
STABILIZE_TIME = 3.0      # seconds to stabilize

# Suppression
SUPPRESSION_MAX = 100
SUPPRESSION_DECAY = 12.0  # per second (tuned from 8.0 per CE/JA2 research)
NEAR_MISS_SUPPRESSION = 0.70  # multiplier on weapon's suppression value
EXPLOSION_SUPPRESSION = 30
ALLY_KILLED_SUPPRESSION = 15

# Cover
COVER_NONE = 0.0
COVER_SOFT = 0.20
COVER_SANDBAG = 0.40
COVER_HARD = 0.60
COVER_FULL = 1.00

# Movement
SPEED_SPRINT = 6.0
SPEED_NORMAL = 4.0
SPEED_CROUCH = 2.0
SPEED_CRAWL = 0.5

# Morale
MORALE_CONFIDENT = 60
MORALE_SHAKEN = 40
MORALE_WAVERING = 20
MORALE_BREAKING = 1
MORALE_RECOVERY_SAFE = 2.0
MORALE_RECOVERY_COVER = 0.5

# Build
BUILD_BUDGET = 200
```
