# Tactical Combat Math & Balancing Reference

A comprehensive reference of combat math, probability mechanics, suppression systems, and balancing parameters across tactical and combat simulations, compiled for **Last Stand: Tactical Combat**.

---

## Executive Summary & Game Mechanics Matrix

| Game / System | Kill Model / HP System | Cover System | Hit Probability / Accuracy Model | Suppression Mechanics | Weapon Roles & TTK |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RimWorld CE** | Anatomical body parts (Torso 40, Head 25, Brain 10). Sharp vs Blunt penetration against RHA (mm) and MPa. | 3D ballistic collision with physical obstacles (height-based). | 100% deterministic physical ballistics. Sway + Spread (deg) + Recoil. No RNG hit-chance roll. | Dedicated meter (0–1050). Projectile near-miss within 3m builds suppression. Forces crouch, run for cover, or hunker down. | Distinct tactical roles. Unarmored TTK: <0.5s (1 burst). Armored TTK: infinite unless AP/Sabot ammo used. |
| **RimWorld Base** | Anatomical body parts (Torso 40, Head 25, Brain 10). AP vs AR roll (0–100). | Multiplicative reduction: Wall 75%, Sandbags/Barricades 55%, Chunks 50%. | Hit = (Acc_shooter)^D * Acc_weapon * (1 - Cover) * Size. | None in base game (added exclusively by mods like CE). | Soft roles. TTK: 3–10s sustained firing due to high miss rates and limb dispersion. |
| **Frozen Synapse** | Binary lethality (1 hit = 1 kill). No health pools. | Low walls provide dramatic aim-speed advantage; ducking grants frontal immunity. | Deterministic reaction/aim clock (T_aim). First to complete aim sequence fires fatal shot. | Implicit: being targeted forces ducking behind cover; losing the reaction race equals instant death. | Strict RPS range hierarchy (Shotgun <6m, Rifle mid-range, Sniper long-range). TTK: 0.2s–2.0s. |
| **XCOM / XCOM 2** | Unified HP pool (Soldiers 4–18 HP; Aliens 3–40 HP) + Flat Armor subtraction. | Directional Defense bonus: Half Cover (+20 Def), Full Cover (+40 Def), Hunker (+30 Def). | Hit = Aim_att + RangeMod - Def_tgt - Cover. Single 1–100 roll for Crit/Hit/Dodge/Miss. | Dedicated ability (Cannons/Rifles): -30 to -50 Aim penalty, triggers reaction fire on movement. | Tier-based (Conventional 3–6, Mag 5–8, Beam 8–10). TTK: 1–3 actions/shots per standard enemy. |
| **Jagged Alliance 2 (1.13)**| Unified HP (1–100) + Bandaged/Bleeding + Stance profile reduction. | Stance reduction (Crouch -20%, Prone -40%) + obstacle Chance To Get Through (CTGT). | CTH = GunCTH + Marks + AimAP - RangePen - TargetMods. | Direct AP deduction + Suppression Shock (-150 CTH) + forced stance drop. Near misses within 1 tile. | High lethality. Burst/Auto-fire delivers massive suppression. TTK: 1–2 headshots or 1 burst. |
| **Real-World Reference**| Human vulnerability: 1–2 center-mass hits incapacitate. | Cover stops bullets; concealment only hides. Angle and defilade dominate. | Angular dispersion (MOA / mrad) + combat stress degradation (accuracy drops 75–90%). | Suppressive threshold: rounds within 1–3m. Fixes movement, degrades fire accuracy, denies observation. | Machine gun suppresses and controls geometry; riflemen/maneuver element flanks and finishes. |


## 1. RimWorld Combat Extended (CE)

Combat Extended replaces RimWorld's RNG hit-chance roll with a fully simulated 3D ballistic and projectile trajectory system.

### 1.1 Suppression Subsystem (CompSuppressable & ProjectileCE)

* **Suppression Meter Bounds:** 0.0 to maxSuppression = 1050.0.
* **Suppression Multiplier:** 2.0 (all applied suppression is multiplied by 2).
* **Decay Delay:** 30 ticks (0.50 seconds after fire stops).
* **Decay Rate:** 4.0 points per tick (240 points per second).
* **Suppression Radius:** 3 tiles in 3D space around bullet trajectory and impact.
* **Minimum Hunker Duration:** 240 ticks (4.0 seconds).
* **Mental Break Trigger:** After >600 ticks (10s) hunkered, 0.1% chance per tick to break (cower, panic flee, berserk).

#### Formulas:
* **Suppression Threshold:**
  SuppressionThreshold = sqrt(max(0, CurrentMood - BreakThresholdMajor)) * 1050 * 0.125
  (Average colonist: ~77.6 points).
* **Hunkering Threshold:**
  HunkerThreshold = SuppressionThreshold * 10 ≈ 776 points.
* **Suppression Applied per Bullet:**
  RawAmount = damageAmountBase * suppressionMultiplier * propsCE.suppressionFactor
  ArmorMod = 1 - clamp(PawnAverageSharpArmor * 0.5 / ArmorPenetrationSharp, 0, 1)
  AddedSuppression = RawAmount * ArmorMod * PawnSuppressability * 2.0

#### Pawn Behavioral States:
1. **Unsuppressed (< 78 pts):** Normal movement, normal accuracy, obeys orders.
2. **Suppressed (78 - 775 pts):**
   * Aim sway increased by 50% (SuppressionSwayFactor = 1.5).
   * Automatically executes RunForCover job toward nearest cover.
   * If in the open with no cover, enters Crouch-Walking (speed reduced ~35%, lower profile).
3. **Hunkered Down (> 776 pts):**
   * Drops prone to the ground for at least 4.0s.
   * Inactive: cannot shoot, aim, or move.
   * Silhouette height drops from 1.75m to ~0.35m (fully protected behind 0.7m sandbags).

### 1.2 Weapon Statistics (Direct from CE Core Patches)

| Weapon | Warmup | Cooldown | Burst | Ticks/Shot | Cyclic RPM | Effective RPM | Range | Spread | Sway | Mag | Reload | Ammo Caliber |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Assault Rifle** | 1.10s | 0.36s | 6 | 4 | 900 | ~200 | 55 | 0.07° | 1.33 | 30 | 4.0s | 5.56x45mm NATO |
| **LMG** (Bren) | 1.30s | 0.56s | 10 | 7 | 514 | ~206 | 62 | 0.05° | 1.37 | 50 | 4.9s | .303 British |
| **Sniper Rifle** | 1.80s | 1.36s | 1 | — | — | ~19 | 75 | 0.05° | 1.35 | 5 | 4.0s | 7.62x51mm NATO |
| **Heavy SMG** | 0.60s | 0.37s | 6 | 6 | 600 | ~244 | 25 | 0.14° | 0.94 | 25 | 4.0s | .45 ACP |
| **Pump Shotgun** | 0.60s | 0.99s | 1 | — | — | ~38 | 16 | 0.14° | 1.31 | 5 | 0.85s/sh | 12 Gauge |
| **Minigun** | 2.10s | 0.35s | 50 | 2 | 1800 | ~730 | 62 | 0.06° | 3.22 | 250 | 9.2s | 7.62x51mm NATO |

### 1.3 Ammunition, Damage & Armor Penetration

| Caliber / Round | Damage | Sharp Pen (mm RHA) | Blunt Pen (MPa) | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **5.56x45mm FMJ** | 14 | 6.0 mm | 34.18 MPa | Standard military ball |
| **5.56x45mm AP** | 9 | 12.0 mm | 34.18 MPa | Pierces light flak |
| **5.56x45mm HP** | 18 | 3.0 mm | 34.18 MPa | High flesh damage |
| **5.56x45mm Sabot** | 7 | 21.0 mm | 44.18 MPa | Pierces Marine Armor |
| **7.62x51mm FMJ** | 20 | 7.0 mm | 66.72 MPa | Battle rifle round |
| **7.62x51mm AP** | 12 | 14.0 mm | 66.72 MPa | Heavy penetration |
| **7.62x51mm Sabot** | 10 | 25.0 mm | 86.28 MPa | Pierces heavy mechanoids |
| **.45 ACP FMJ** | 12 | 3.5 mm | 10.86 MPa | Subsonic pistol round |
| **12 Gauge Buckshot** | 8 | 4.0 mm | 4.52 MPa | 9 pellets (Total 72 dmg) |
| **12 Gauge Slug** | 28 | 6.0 mm | 85.20 MPa | Massive blunt kinetic force |

### 1.4 Accuracy Model & TTK in CE
* **Accuracy Formula:** Sway = max(0, (4.5 - ShootingAccuracy) * SwayFactor / SightsEfficiency). Suppressed sway = Sway * 1.5. Spread = weapon ShotSpread (deg).
* **TTK Unarmored:** Torso = 40 HP. 5.56mm deals 14 dmg -> 3 hits kill, 2 hits cause incapacitating pain shock (>80%). Burst of 6 rounds takes 0.33s. **TTK < 0.5s**.
* **TTK Headshot:** Head = 25 HP, Brain = 10 HP. 1 hit kills instantly. **TTK = 0.0s**.
* **TTK Armored (Marine Armor 15-20mm RHA):** FMJ (6mm pen) completely deflects (0 sharp dmg). **TTK = infinite** without AP/Sabot. Sabot (21mm pen) kills in 3-4 hits (**TTK ~1.0s**).

---

## 2. RimWorld Base Game

### 2.1 The Hit Chance Formula

Hit Chance = (Shooter Accuracy)^Distance * Weapon Accuracy(Distance) * (1 - Cover Effectiveness) * BodySize * Weather

* **Shooter Accuracy (per-tile):**
  * Skill 0: 86% per tile (0.86^10 = 22.1% at 10 tiles)
  * Skill 8: 96% per tile (0.96^10 = 66.5% at 10 tiles, 0.96^25 = 36.0% at 25 tiles)
  * Skill 20: 99% per tile (0.99^10 = 90.4% at 10 tiles, 0.99^25 = 77.8% at 25 tiles)
* **Weapon Accuracy:** Interpolated between Touch (3 tiles), Short (12 tiles), Medium (25 tiles), Long (40 tiles).
* **Cover Effectiveness:**
  * Wall (peeking/leaning): 75% cover (Multiplier = 0.25)
  * Sandbags: 55% cover (Multiplier = 0.45)
  * Barricades: 55% cover (Multiplier = 0.45)
  * Rock Chunks: 50% cover (Multiplier = 0.50)
  * Tree: 25% cover (Multiplier = 0.75)
  * Low Bushes: 20% cover (Multiplier = 0.80)

### 2.2 Armor Penetration & Damage Calculation Formula

Effective AR = Armor Rating - Weapon Armor Penetration
The game rolls a random uniform integer R in [0, 100]:
1. **Deflection (0 damage):** R <= 0.5 * Effective AR
2. **Mitigation (Half damage, converted to Blunt):** 0.5 * Effective AR < R <= Effective AR
3. **Full Penetration (Full damage):** R > Effective AR

### 2.3 Pawn Body Part HP Values
* **Vital Parts (Pawn dies immediately if destroyed):**
  * Torso: 40 HP
  * Head: 25 HP
  * Brain: 10 HP
  * Neck: 25 HP
  * Heart: 15 HP
  * Liver: 20 HP
* **Other Major Parts:**
  * Limbs (Arms/Legs): 30 HP each
  * Shoulders: 25 HP each
  * Hands/Feet: 20 HP each
  * Lungs/Kidneys: 15 HP each
* **Incapacitation (Downed):** Pain >= 80%, Consciousness < 30%, or loss of mobility (both legs/spine).

---

## 3. Frozen Synapse

### 3.1 Kill & Damage Model
* **Lethality:** Pure binary 1-shot-kill (1-hit kill). No HP bars, no chip damage, no bleeding.
* Units have 0 hit point pool; a single landed projectile kills instantly.

### 3.2 Duel Resolution & The Aim Clock
Duels are deterministic races governed by an aiming timer (T_aim). When two opposing units detect each other, both clocks begin counting down; the unit reaching 0 first fires and kills.

* **Stillness vs. Movement:**
  * Stationary units have baseline minimum aim time (~0.5s for rifles).
  * Moving units suffer a reaction/aim penalty (+0.5s to +1.0s). Stillness beats movement in 100% of head-to-head duels.
* **Facing & Orientation:**
  * Units with an Aim command facing the enemy engage immediately.
  * Units facing away must complete angular turning before aim time begins.
* **Cover & Ducking:**
  * **Low Cover:** Provides a major detection and aim speed advantage. Standing behind low cover facing an enemy in open ground wins the duel 100% of the time at equal range.
  * **Ducking behind Cover:** Completely blocks line of sight over the low wall; unit is 100% immune to direct frontal fire, but cannot return fire.
* **Weapon Range Hierarchy:**
  * **Shotgun:** Near-instant aim at close range (<6 tiles), 0% effectiveness at medium/long.
  * **Machine Gun / Assault Rifle:** Balanced aim time (~0.5s), effective across medium ranges.
  * **Sniper:** Long aim time (~1.5s–2.0s), infinite range, precise single-shot elimination.

---

## 4. XCOM / XCOM 2

### 4.1 Hit Chance Formula & Single-Roll System

Hit Chance = Base Aim + Range Modifier - Target Defense - Cover Defense

* **Single-Roll Resolution (XCOM 2):** Single roll from 1 to 100 determines all outcomes:
  1. Roll <= Crit Chance -> Critical Hit
  2. Else if Roll <= Hit Chance -> Normal Hit
  3. Else if Roll <= Hit Chance + Target Dodge -> Graze (Half Damage)
  4. Else -> Miss

### 4.2 Cover Values
* **Open / Flanked:** +0 Defense, +40% Critical Hit vulnerability.
* **Half Cover:** +20 Defense.
* **Full Cover:** +40 Defense.
* **Hunker Down:** +30 Defense (+40 in half cover), +50 Dodge, complete Crit immunity.
* **Elevation / High Ground:** +20 Aim for attacker shooting down.

### 4.3 Weapon Damage Across Tiers

| Weapon Class | Conventional (Tier 1) | Magnetic (Tier 2) | Beam / Plasma (Tier 3) | Ammo | Crit Bonus |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Assault Rifle** | 3 – 5 (avg 4) | 5 – 7 (avg 6) | 7 – 9 (avg 8) | 4 | +2 / +3 / +4 |
| **Shotgun** | 4 – 6 (avg 5) | 6 – 8 (avg 7) | 8 – 10 (avg 9) | 4 | +3 / +4 / +5 |
| **Cannon** (LMG) | 4 – 6 (avg 5) | 6 – 8 (avg 7) | 8 – 10 (avg 9) | 3 | +2 / +3 / +4 |
| **Sniper Rifle** | 4 – 6 (avg 5) | 6 – 8 (avg 7) | 8 – 10 (avg 9) | 3 | +2 / +3 / +4 |
| **Pistol** | 2 – 3 (avg 2.5) | 3 – 4 (avg 3.5) | 4 – 6 (avg 5) | inf | +1 / +2 / +3 |
| **Frag Grenade** | 3 – 4 (shreds 1 armor)| 4 – 5 (Alien Grenade) | 5 – 6 (Plasma Grenade) | 1 | 0 |

### 4.4 HP Values (Soldiers vs Aliens)
* **XCOM Soldiers:**
  * Rookie: 4–5 HP, 0 Armor
  * Sergeant (Plated Armor): 8–10 HP, 1 Armor
  * Colonel (Powered Armor): 14–18 HP, 2 Armor
* **Aliens:**
  * ADVENT Trooper: 3–4 HP, 0 Armor
  * ADVENT Officer: 7 HP, 1 Armor
  * Sectoid: 8–10 HP, 0 Armor
  * Viper: 8 HP, 0 Armor, 35 Dodge
  * Muton: 9 HP, 2 Armor, 10 Defense
  * ADVENT MEC: 7–9 HP, 2 Armor
  * Berserker: 24 HP, 0 Armor
  * Andromedon: 17 HP, 4 Armor (+ Robot shell 19 HP, 4 Armor)
  * Sectopod: 32–40 HP, 5–6 Armor

---

## 5. Jagged Alliance 2 (JA2 / JA2 v1.13)

### 5.1 Suppression Mechanics (v1.13)
* **Near-Miss Trigger:** Bullets passing within 1 tile of a character add suppression points.
* **Volume of Fire Scaling:** Burst and automatic fire deliver multiple consecutive checks.
* **Resistance:** Based on Experience Level + Morale + Personality (Dauntless vs Coward).
* **Effects:**
  1. **Direct AP Loss:** Drains AP immediately and rolls over into next turn (can pin at 0 AP).
  2. **Suppression Shock:** ShockModifier = (ShooterShock * 100) / MaxShock, inflicting up to -150 CTH penalty.
  3. **Forced Stance Drop:** Standing -> Crouching -> Prone -> Cowering.

### 5.2 Morale System Values (0 to 100 scale, Baseline = 50)
* **Event Impacts:**
  * Kill enemy: +5 to +10
  * Teammate killed: -15 to -25
  * Teammate wounded: -5 to -10
  * Friendly fire: -10
  * Direct damage: -2 to -5 (scaled by % max HP lost)
  * Suppression: -1 Morale per 2 AP lost to suppression
  * Leadership aura: AuraBonus = (Leadership - 50) / 10

### 5.3 Cover System
* **Stance Profile:** Standing (100% profile, 0% bonus), Crouching (60% profile, -20% hit chance), Prone (20% profile, -40% hit chance).
* **Chance To Get Through (CTGT):** 3D raycasting through obstacle heights and material hardness (wood, brick, reinforced concrete).

---

## 6. Real-World Reference & Tactical Doctrine

### 6.1 Rounds Fired Per Casualty in Modern Combat
* **World War II:** ~25,000 – 45,000 rounds per casualty.
* **Korean War:** ~30,000 – 80,000 rounds per casualty.
* **Vietnam War:** ~50,000 – 200,000+ rounds per casualty.
* **Iraq / Afghanistan:** ~60,000 – 300,000+ rounds per casualty.
* **Direct Firefights (Tactical Contact):** **500 to 2,500 rounds per casualty**.
* **Combat Snipers:** **1.3 to 1.7 rounds per casualty**.
* **Why the ratio is thousands-to-one:** Over 90% of small arms ammunition is fired as area suppression against suspected cover (windows, tree lines, berms) to deny movement and vision, rather than aimed fire at exposed human targets.

### 6.2 Tactical Doctrine: How Suppression Actually Functions
U.S. Army (**FM 3-21.8**) and British infantry doctrine organize tactical combat around the **Four Fs**:
1. **FIND:** Spot enemy avenues and positions.
2. **FIX:** Heavy suppressive fire (Base of Fire / Machine Guns) forces enemy into deep cover, cutting their vision and rendering return fire erratic and ineffective.
3. **FLANK:** Maneuver element moves uncontested around the fixed enemy position.
4. **FINISH:** Assault element destroys the fixed enemy at close range with grenades and direct fire.
*Key Takeaway:* Machine guns are **geometry denial tools**, not precision killers. Their job is to dominate open ground and pin enemy units.

---

## 7. Recommended Concrete Model for Last Stand Prototype

`
+-------------------------------------------------------------+
|               LAST STAND TACTICAL ENGINE MODEL              |
+-------------------------------------------------------------+
|                                                             |
|  [Rounds in Flight] ---> Near Miss (<2.5m) ---> +Suppression|
|          |                                             |    |
|          v                                             v    |
|  [Cover Check]                                [Meter 0-100] |
|   - Low: 60% Block                             - 0-29: Norm |
|   - High: 80% Block                            - 30-69: Pin |
|   - Flank: 0% Block                            - 70+: Hunk  |
|          |                                                  |
|          v                                                  |
|  [Damage / Armor Check]                                     |
|   Torso: 40 HP | Head: 20 HP (Lethal) | Limbs: 25 HP        |
+-------------------------------------------------------------+
`

### 7.1 Suppression Meter Formulas (0 to 100 Scale)
* **Meter Range:** 0 to 100 per pawn.
* **Near-Miss Accumulation:** Bullet passing within 2.5m adds CaliberBase * (1.0 - dist / 2.5).
  * Rifle (5.56mm): 4 pts.
  * MG (7.62mm): 8 pts.
  * Grenade/Explosion: 50 pts.
* **Suppression Decay:** After 0.75s without incoming fire, decays at **15 pts/sec**.
* **States:**
  * **Normal (< 30):** Full speed, normal aim.
  * **Suppressed / Pinned (30–69):** -35% movement speed, +50% aim time, -35% accuracy, drops to involuntary crouch.
  * **Hunkered Down (>= 70):** Inactive (cannot shoot or move), drops flat behind cover (immune to frontal fire over low cover), stays hunkered min 3.0s.

### 7.2 Cover Values
* **Low Cover (Sandbags / Barricades):** 60% block chance (0.40 hit multiplier).
* **High Cover (Walls / Bunkers):** 80% block chance (0.20 hit multiplier).
* **Flanked (>45° angle):** 0% cover bonus.

### 7.3 Prototype Weapon Balancing Archetypes

| Weapon | Dmg/Hit | Burst Count | Burst RPM | Cycle Time | Eff Range | Supp/Burst | TTK (Unarmored Open) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Assault Rifle** | 15 HP | 4 | 750 RPM | 1.4s | 30m | 16 pts | 0.8s (2 hits to kill) |
| **Machine Gun** | 18 HP | 10 | 900 RPM | 2.2s | 45m | 60 pts (Insta-Pin) | 0.5s (2 hits to kill) |
| **Sniper Rifle** | 60 HP | 1 | — | 2.5s | 60m | 15 pts | 0.0s (1 hit instant kill)|
| **Shotgun** | 8x8 (64 HP) | 1 | — | 1.1s | 12m | 25 pts | 0.0s (Point blank lethal)|
