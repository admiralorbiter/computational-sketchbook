# Last Stand: Tactical Combat — Game Design Document

> **Working document** — captures design intent, not final specifications.

---

## 1. Vision

### One-Sentence Pitch
A tactical defense game where you engineer a battlefield, write a battle plan, then fight to survive when reality collides with your preparation.

### The Hook
**Build the defense. Write the battle plan. Then find out what you forgot.**

### What This Is NOT
- Not a colony sim (no farming, cooking, cleaning, hauling)
- Not a pure tower defense (you have direct micro control)
- Not a pure autobattler (you intervene during combat)
- Not a base-builder (no bedrooms, butcher tables, recreation)
- Not wealth-scaled (don't punish the player for being successful)

### What This IS
- RimWorld combat × RTS control × tower-defense preparation × wargame scenario sandbox
- A game where the AI handles competent routine execution; the player handles exceptional decisions
- A system where suppression, cover, line-of-sight, and morale interact to create emergent situations
- A game you can replay the same scenario 10 times and learn something new each time

---

## 2. Core Loop

### Five-Phase Battle Loop

```
Briefing → Preparation → Orders → Battle → After-Action
                                                  ↓
                                            RETRY / NEXT
```

#### Phase 1: Briefing
The player receives incomplete intelligence about an incoming threat:
- Enemy type / faction
- Estimated force strength
- Likely avenues of approach
- Mission objective
- Terrain and map layout
- Weather / time of day
- Special intel (if available)
- Intelligence confidence percentage

Example:
```
Scenario: Relay Station 17
Hold relay for 8 minutes.
Estimated opposition: 30–45 infantry.
Armored support possible.
Primary approach: east.
Intelligence confidence: 71%.
```

#### Phase 2: Preparation
The "base building" phase, compressed entirely into military engineering.

Constraints:
- Limited money/materials
- Limited manpower
- Limited setup time

Buildable items (full game vision):
- Barricades, sandbags, walls
- Trenches, firing positions
- Doors (powered and manual)
- Barbed/razor wire
- Mines (anti-personnel, directional)
- Remote charges
- Motion sensors, cameras
- Floodlights
- Ammunition caches
- Medical stations
- Smoke/gas dispensers
- Automated turrets
- Fallback position markers
- Decoys (loudspeakers, etc.)

#### Phase 3: Orders
The player issues doctrinal orders — the opening battle plan.

Initial command vocabulary:
- **Hold here** — defend this position
- **Watch this sector** — monitor and engage within a defined arc
- **Suppress this area** — lay down suppressive fire
- **Protect this unit/position** — prioritize defense of a target
- **Fallback here** — designate retreat position

Advanced (future) — conditional doctrine:
```
IF enemies > 5 in Sector B
AND suppression < 50%
THEN throw smoke
AND fallback to Position Charlie
```

Design goal: architecture supports the conditional system from day one, even though the UI starts simple.

#### Phase 4: Battle
Real-time combat. This is where player micro lives.

The player can:
- Pause / slow motion
- Select and command units (RTS-style)
- Issue new orders
- Activate abilities
- Detonate charges
- Open/close doors
- Deploy smoke
- Commit reserves

Key principle: **If existing orders are reasonable, units execute autonomously.** The player intervenes for exceptional decisions.

#### Phase 5: After-Action
Post-battle analysis:
- Timeline of events
- Casualty report
- Ammunition expenditure
- Kill/incapacitation stats
- Breach locations
- Unit movement heatmaps
- Enemy path visualization
- Morale break points
- Sector compromise timeline
- Critical event callouts

Then: **RETRY SCENARIO** or **NEXT MISSION**

---

## 3. The Micro Philosophy

### The Boundary
The AI handles **competent routine execution**. The player handles **exceptional decisions**.

### What Units Do Autonomously
- Use nearby cover
- Step away from grenades
- Reload
- Select reasonable targets within their orders
- Avoid friendly fire
- Duck when suppressed
- Reposition a few meters within their assigned area

### What Units Do NOT Decide Autonomously
- Abandon a flank
- Pursue fleeing enemies
- Reposition the entire squad
- Expend scarce explosives/abilities
- Open gates
- Detonate minefields
- Commit reserves
- Strategic retreats

**These belong to the player.** This boundary is one of the most important design decisions in the game.

### Skill Ceiling
- **New player:** "Alpha, defend here."
- **Expert player:** "Alpha defend here, MG covers this arc, rifles cover approaches, medic behind hard cover, fallback to Charlie if breached, suppress on contact..."
- During combat, expert micro squeezes more performance. That's good.

---

## 4. Control Language

Steal StarCraft's proven control scheme:

| Input | Action |
|-------|--------|
| Left-click | Select |
| Drag box | Multi-select |
| Shift+click | Add/remove from selection |
| Ctrl+1-9 | Assign control group |
| 1-9 | Recall control group |
| Right-click | Move / context command |
| A+click | Attack-move |
| S | Stop |
| H | Hold position |
| Double-click | Select all of unit type |
| Tab | Cycle subgroups |

Game-specific orders:

| Key | Order |
|-----|-------|
| W + drag arc | **Watch Sector** — define firing arc |
| F + click | **Suppress Area** — lay suppressive fire |
| R + click | **Fallback** — designate retreat point |
| G | Throw grenade |
| K | Deploy smoke |
| D | Detonate (context) |

### Watch Sector (Signature Mechanic)
Select soldiers → press W → drag an arc from their position.

```
                  ┌──────────────
             ╱    │
          ╱       │ WATCH AREA
       ╱          │
    [R][R][MG]    │
       ╲          │
          ╲       │
```

The selected units understand:
- This is my firing sector
- Don't turn around for irrelevant enemies
- Don't leave cover to chase
- Prioritize enemies inside this arc
- Suppress groups rather than snipe individuals (for MG)
- Another squad owns the adjacent sector

Future parameters per watch sector:
- Engagement range
- Priority targets
- Fire discipline (conserve ammo / free fire)
- Hold vs. fallback behavior

---

## 5. Combat Systems

### 5.1 Line of Sight & Cover
- Raycasting from unit to target
- Cover provides percentage-based protection
- Hard cover (walls, concrete) vs soft cover (sandbags, furniture)
- Flanking negates cover advantage
- Elevation advantage (future)

### 5.2 Suppression
**Potentially more important than damage.**

Near misses and volume of fire produce suppression:
- Suppressed units lose accuracy
- Heavily suppressed units seek cover involuntarily
- Fully suppressed units hunker down (combat ineffective)
- Suppression decays over time without incoming fire

This makes the MG's role distinct: it doesn't necessarily kill efficiently, but it **dominates open ground**.

### 5.3 Weapon Roles

| Weapon | Role | Strength | Weakness |
|--------|------|----------|----------|
| Machine gun | Suppression, area denial | Dominates open avenues | Slow to reposition, ammo hungry |
| Rifle | Versatile engagement | Accurate, mobile | Lower suppression output |
| Sniper | Precision elimination | Kills officers, breachers | Low fire rate, poor CQB |
| Shotgun | Close quarters | Devastating in breaches | Terrible at range |
| Flamethrower | Area denial | Creates fire/panic | Short range, friendly fire risk |
| Grenade launcher | Force displacement | Breaks cover positions | Limited ammo, indirect |

### 5.4 Damage
- Health points with location (future: limbs, bleeding)
- Armor reduces damage by type
- Incapacitation vs. death distinction
- Wounded units are slower, less accurate
- Downed units can be rescued by medics

### 5.5 Enemy Morale (Critical System)
- Enemies value their own lives
- Watching allies die affects behavior
- Suppression degrades morale
- Losing their commander matters
- "Three people died entering that doorway" affects the fourth person
- Morale breaks cause: retreat, surrender, routing, panic fire
- Different enemy types have different morale profiles

---

## 6. Enemy AI

### Three-Level AI Architecture

#### Level 1: Individual AI
- Where should I stand?
- Which visible enemy should I shoot?
- Should I crouch?
- Am I suppressed?
- State machine + utility scoring

#### Level 2: Squad AI
- What sector are we attacking?
- Are we advancing or pinned?
- Who covers whom?
- Breach or flank?

#### Level 3: Commander AI
- What's the objective?
- Where is the defense weak?
- Should reserves commit?
- Should we retreat and regroup?
- Adapt to observed defenses

### Reactive AI (Anti-Killbox)
Don't ban killboxes. Make the AI learn during the battle:
- "Everyone who entered that hallway died." → Stop sending people that way.
- Identify lightly defended sectors
- Shift assault direction
- Use smoke/suppression to cover advances
- Breach walls if doors are death traps

### Enemy Squad Composition
Raiding parties may include:
- Assault team
- Suppression team
- Breachers
- Marksmen
- Medic
- Reserve
- Commander

---

## 7. Threat Archetypes

Different enemy types attack your assumptions differently:

| Type | Behavior | Challenge |
|------|----------|----------|
| **Horde** | Many, dumb individually | Traps and funnels shine |
| **Predators** | Fast, climb, avoid exposure | Walls aren't sufficient |
| **Human Raiders** | Cover, smoke, suppress, breach, retreat | Requires proper tactics |
| **Machines** | Ignore morale and gas, systematic | Vulnerable to EMP |
| **Giant Creature** | Destroys walls, ignores killbox geometry | Forces adaptation |

This keeps the sandbox stable while the problem changes.

---

## 8. Interactive Systems (Full Vision)

Not 400 separate mechanics. ~8 underlying simulations that interact everywhere.

### 8.1 Fire
Creates: heat, light, smoke, panic, structural damage.
- Deliberately starting a fire illuminates attackers but may obscure your shooters
- Spreads along flammable materials

### 8.2 Smoke
- Blocks line of sight
- Airflow matters (doors, fans, wind move it)
- Deliberately smoke a corridor before retreating through it

### 8.3 Gas
- Follows airflow physics
- Door + vent + fan + gas = system, not a dedicated "gas trap building"
- Different gas types (tear gas, poison, incendiary)

### 8.4 Electricity
- Power runs through physical lines
- Destroy a transformer: lights die, powered doors fail, turrets stop, sensors stop
- Backup generators suddenly matter

### 8.5 Structural Integrity
- Explosives damage supports
- Walls collapse, creating debris/new cover
- Collapsed defensive position might accidentally create a fantastic barricade
- The battlefield physically changes during combat

### 8.6 Sound
- Gunfire creates sound that travels
- Enemies investigate sound sources
- Suppressed weapons, alarms, generators, explosions, decoy speakers all interact
- Loudspeaker in abandoned building → attract horde → collapse building

### 8.7 Visibility
- Units have vision cones
- Lighting matters (floodlights, darkness)
- Spotters, cameras, drones, motion sensors, thermal vision
- Detection → communication → engagement chain
- Kill the radio relay → squads lose shared targeting info

### 8.8 Weather / Environment
- Rain, wind, fog affect visibility, fire, sound
- Time of day affects lighting
- Terrain affects movement speed

---

## 9. Meta-Game Structure

### No Colony Sim — A Persistent Roster
Not a colony. More like a company/barracks.

12 persistent soldiers who:
- Develop skills
- Gain traits / battlefield experience
- Suffer injuries, lose limbs
- Form relationships
- Panic differently
- Specialize in weapons

Between missions: **Personnel / Equipment / Contracts / Research**

No farming. No cooking. No cleaning. No hauling.

But: "Alicia, your squad leader from the last seven missions, just got trapped behind a collapsed wall." → Suddenly I care.

RimWorld storytelling without RimWorld chores.

### Threat Selection (Not Wealth Scaling)
Don't punish success. Make threat legible:

```
Contract: Blackwater Outpost
Threat rating: 7
Expected force: 80–120
Reward: $42,000
Intelligence confidence: 72%
```

Player chooses difficulty. Uncertainty exists within it.

### Mission Objectives (Beyond "Kill Everybody")
- Hold for X minutes
- Protect evacuating civilians
- Keep a structure operational
- Recover downed people outside perimeter
- Hold two locations simultaneously
- Delay then withdraw
- Enemies want your supplies — maybe abandon the warehouse to preserve soldiers

---

## 10. Intelligence Layer (Future)

Before raids:
- Recon reports with confidence levels
- Spend resources to improve intel
- Drone recon reveals enemy equipment/composition
- Counter-intelligence possibilities
- Preparing against uncertainty, not just known quantities

---

## 11. Replay System

If simulation is deterministic-ish (fixed ticks, seeded RNG):
- Store: scenario seed + initial placement + build decisions + player commands + timestamps
- Full battle replay
- Heatmaps, enemy paths, command timeline
- Rewind to critical moments
- "Restart from planning using same enemy seed"
- Automated balance testing (run Battle 001 10,000 times)

---

## 12. Three-Layer Design Philosophy

```
Layer 1 — ENGINEERING
  What battlefield did I construct?
  Walls, obstacles, traps, power, sight lines.

Layer 2 — DOCTRINE  
  What have I told everyone to do?
  Sectors, rules of engagement, fallback plans, reserves.

Layer 3 — COMMAND
  What do I change now that the plan is failing?
  Move reserves. Authorize retreat. Detonate the bridge.
  Open the western gate. Deploy smoke.
```

Most of the battle should be: "Oh shit oh shit oh shit… YES! The plan worked."

Future Layer 4 — **INTELLIGENCE**: What do I know before the battle starts, and do I trust it?
