# Tuning Notes — Research Cross-Reference

> Comparing our combat-math.md values against reference data from
> RimWorld (base + CE), XCOM, Frozen Synapse, Jagged Alliance 2, and real-world doctrine.

---

## Validation Summary

| System | Our Value | Reference Range | Verdict |
|--------|-----------|-----------------|---------|
| **Rifle TTK (exposed)** | ~4.0s | CE: <0.5s, RW base: 3–10s, XCOM: 1–3 actions | ✅ Right for our game. Longer than CE but matches RW base. Gives time for decisions. |
| **MG role** | Suppression-primary | CE: same, Real-world FM 3-21.8: "geometry denial tools" | ✅ Perfectly validated by doctrine |
| **Cover (sandbag)** | ×0.50 hit chance | RW base: ×0.45, XCOM half-cover: -20 aim, CE: physical | ✅ Very close to RW base |
| **Cover (hard/wall)** | ×0.35 hit chance | RW base: ×0.25, XCOM full-cover: -40 aim | ✅ Slightly more generous than RW (intentional — peek/lean) |
| **Suppression decay** | 8 pts/sec | CE: 240 pts/sec (but 1050 scale), Research rec: 15 pts/sec | ⚠️ May be too slow — see below |
| **Suppression thresholds** | 5 levels (0–100) | CE: 3 states (unsuppressed/suppressed/hunkered), JA2: continuous | ✅ More granular than CE, good for gameplay legibility |
| **Unit HP** | 100 flat | CE: body parts (40 torso), RW base: body parts, XCOM: 4–18 | ✅ Simpler is correct for POC |
| **Shotgun range model** | Devastating <3, useless >10 | Frozen Synapse: hard cutoff at ~6, CE pump: 16 tiles | ✅ Our falloff curve is right |
| **Near-miss suppression** | 70% of weapon value | CE: within 3-tile radius, JA2: within 1 tile | ✅ Good abstraction of the spatial concept |

---

## Recommended Adjustments Based on Research

### 1. Suppression Decay — Consider Increasing

**Current:** 8 pts/sec → 12.5s from pinned to clear.

**Research suggests:** CE decays at 240/sec on a 1050 scale (normalized: ~23/sec on 100 scale). Research recommendation: 15 pts/sec.

**Problem with 8/sec:** Suppression lingers too long. A single MG burst that pins someone keeps them effectively out of the fight for 10+ seconds even after the MG shifts targets. That might feel punishing rather than tactical.

**Recommendation:** Start at **12 pts/sec**. Test both:
- At 8/sec: suppression is very sticky, MG dominates harder
- At 12/sec: suppression is responsive, requires sustained fire to maintain

This is the **single most important tuning knob** in the game. It controls:
- How powerful the MG feels
- How fast enemies recover between bursts
- Whether suppression is a death sentence or a tactical tool
- The tempo of the entire battle

```gdscript
# In game_constants.gd — easy to change
const SUPPRESSION_DECAY: float = 12.0  # was 8.0, try 12.0
```

### 2. Near-Miss Window — The 1.5× Multiplier

**Current:** Near miss if roll ≤ hit_chance × 1.5 (combat.gd line 42).

**Issue:** This means a 70% accuracy weapon has near misses only in the 70–105% range (capped at 100), so effectively only rolls between 0.70 and 1.00 are near misses (30% chance). At 35% accuracy (MG), near misses happen on rolls between 0.35 and 0.525 (17.5% chance).

**Research:** CE applies suppression to any bullet within 3 tiles of a target. JA2 uses any bullet within 1 tile.

**Recommendation:** Widen the near-miss window, especially for high-volume weapons:

```gdscript
# In combat.gd — change the near-miss calculation
# Current: hit_chance * 1.5
# Better: hit_chance + 0.30 (flat bonus)
elif roll <= hit_chance + 0.30:
    # Near miss
```

This gives the MG (0.35 accuracy) near misses on rolls 0.35–0.65 (30% chance), much better for suppression output. Already what combat-math.md specifies — just needs to match in code.

### 3. Real-World Doctrine — The Four Fs

The research surfaced FM 3-21.8's "Four Fs" framework. This maps beautifully to our game:

| Doctrine | Your Game |
|----------|-----------|
| **FIND** — Spot enemy | Watch Sector orders, perception system |
| **FIX** — Suppress enemy | MG suppression, Suppress Area order |
| **FLANK** — Maneuver around | Player moves riflemen around the fixed enemy |
| **FINISH** — Assault at close range | Shotgunner + grenades at close range |

This could be taught in a tutorial or briefing text without being heavy-handed.

### 4. Morale Events — JA2 Has Good Numbers

Our morale spec is reasonable but JA2's numbers are well-tested:

| Event | Ours | JA2 | Notes |
|-------|:---:|:---:|-------|
| Ally killed (same squad) | -12 | -15 to -25 | Ours might be too gentle |
| Ally killed (nearby) | -8 | -15 to -25 | Same concern |
| Suppression drain | -5/sec pinned | -1 per 2 AP lost | Different systems, similar feel |
| Kill enemy | +10 | +5 to +10 | Aligned |

**Recommendation:** Increase ally-death morale impact to -15 (same squad) and -10 (nearby). Makes routing feel more dramatic and rewards targeting clustered squads.

### 5. Frozen Synapse's Lesson — Stillness Should Win

Frozen Synapse's deterministic "aim clock" creates a powerful rule: a stationary unit behind cover always beats a moving unit. Our system already models this through MovementMod (×0.50 for normal move, ×0.15 for sprint), but it's worth emphasizing:

**A defender standing still behind a sandbag should reliably defeat an attacker running across open ground.**

Quick check:
```
Defender (rifle, stationary, sandbag): 0.70 base, ×1.0 move = 0.70 accuracy
Attacker (rifle, sprinting, exposed): 0.70 × 0.15 move = 0.105 accuracy

Defender DPS: 2.0 × 0.70 × 18 = 25.2
Attacker DPS: 2.0 × 0.105 × 18 × 0.60 (sandbag dmg reduction) = 2.27

TTK defender kills attacker: 100/25.2 = 4.0s
TTK attacker kills defender: 100/2.27 = 44.1s
```

**Ratio: 11:1 in defender's favor.** That's correct. Charging a prepared position should be suicide. The attacker needs smoke, suppression, or a different approach.

### 6. XCOM's Graze — Worth Considering Later

XCOM 2's dodge/graze system (half damage on near-hit) adds a nice middle ground between hit/miss. For the POC, binary hit/miss is fine. But for v2:

```
Roll ≤ HitChance:           HIT (full damage)
Roll ≤ HitChance + 0.15:    GRAZE (50% damage, 50% suppression)
Roll ≤ HitChance + 0.30:    NEAR MISS (0 damage, 70% suppression)
Roll > HitChance + 0.30:    WIDE MISS (nothing)
```

This would make combat feel less binary and create more "close call" moments.

---

## Things We Got Right

1. **MG as suppression tool** — Validated by CE, JA2, and real-world doctrine. Our MG's 35% accuracy / 600 RPM / 5 suppression per round profile correctly makes it a lane-denial weapon.

2. **100 HP flat pool** — CE's body-part system is realistic but complex. XCOM's 4–18 HP creates binary "alive/dead" swings. Our 100 HP gives granular health degradation without anatomical complexity. Right for a POC.

3. **Five suppression levels** — More legible than CE's continuous meter, more nuanced than XCOM's binary "suppressed or not." Players can intuitively understand "PINNED" vs "LIGHT."

4. **Shotgun range curve** — Our steep falloff (devastating at 3, useless at 10) matches Frozen Synapse's hard range hierarchy. Shotguns that work everywhere are boring. Shotguns that own doorways are interesting.

5. **Cover as directional** — RimWorld base and CE both use positional cover relative to the shooter. Our flanking-negates-cover rule creates the same tactical geometry.

6. **Data-driven design** — CE's success as a mod proves that separable weapon/ammo/armor data is essential for balance iteration.

---

## The One Number That Matters Most

If you could only tune **one value** during playtesting, tune **SUPPRESSION_DECAY**.

- Too low (4/sec): MG is god. One burst pins everything forever. Attackers never reach the wall.
- Too high (20/sec): suppression evaporates instantly. MG feels pointless. Might as well just have six riflemen.
- Sweet spot (8–15/sec): MG creates windows of opportunity. Sustained fire maintains suppression. Bursting and shifting targets creates tactical rhythm.

The research validates that this single parameter controls the entire feel of the combat system, just as it does in CE, where suppression tuning has been one of the most debated aspects of the mod for years.
