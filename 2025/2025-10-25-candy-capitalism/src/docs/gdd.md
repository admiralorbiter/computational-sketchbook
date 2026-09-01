# Candy Capitalism - Game Design Document

## High Concept

A Halloween-themed economic manipulation game where you play as a market demon (the "invisible hand") influencing trick-or-treating children to manipulate a candy-based economy through possession, rumors, supply control, and strategic interference. Master both chaos and profit as you exploit emergent trading behaviors in a living candy market.

## Core Pillars

1. **Emergent Chaos** - Simple AI rules create complex, unpredictable economic behaviors
2. **Indirect Control** - You suggest and influence rather than directly command
3. **Information Warfare** - Manipulate beliefs, spread rumors, control knowledge
4. **Supply & Demand Mastery** - Control both sides of the market equation
5. **Systems Over Graphics** - Deep simulation with minimal UI requirements

## Target Scope

- **Development Time**: 3-4 months (solo developer)
- **Engine**: Pygame
- **Art Style**: Simple 2D sprites (custom art, pixel art or minimalist vector)
- **Complexity**: Backend-heavy with minimal UI chrome

---

## Core Gameplay Loop

### Minute-to-Minute
1. Observe kids autonomously trick-or-treating and trading
2. Possess one kid or spread one rumor
3. Watch immediate effects ripple through local trades
4. Switch possession or spread another rumor

### Hour-to-Hour
1. Track candy price trends across the neighborhood
2. Identify emerging market leaders and vulnerable kids
3. Execute multi-step manipulation plans (debt cascades, rumors, hoarding)
4. React to unexpected emergent behaviors

### Session-to-Session
1. Unlock new manipulation powers based on chaos caused
2. Face increasing economic complexity (kids learn, adapt)
3. Complete scenario objectives (crash specific markets, create monopolies, etc.)

---

## Core Systems

### 1. NPC Kid AI System

**Kid Attributes:**
- **Personality Type**: Value Investor, Momentum Trader, Hoarder, Social Trader, Panic Seller
- **Preferences**: Array of candy type preferences (0.0-1.0 per candy type)
- **Mood**: Happy, Neutral, Anxious, Greedy (affects trading behavior)
- **Trust Level**: How much they believe rumors (0-100)
- **Wallet**: Current candy holdings by type
- **Debt**: Owes candy to other kids
- **Knowledge**: What they believe about candy values (can differ from reality)
- **Memory**: Recent trades, who they trust, who scammed them
- **Social Network**: Friend/enemy relationships with other kids
- **Personal Goal**: Simple objective that drives behavior (e.g., "collect all chocolate types", "get 10 romantic candies")
- **Trading Bloc**: Membership in informal cartel/alliance groups

**Trading AI Logic:**
```
Every tick (2-3 seconds):
1. Assess needs based on preferences
2. Check believed values of candy vs real values
3. Find potential trading partners within range
4. Propose trades based on personality type:
   - Value Investors: Trade when they believe value gap exists
   - Momentum: Trade toward rising-price candies
   - Hoarders: Accumulate favorites, rarely trade
   - Social: Trade with friends even at bad rates
   - Panic: Sell when prices drop or rumors spread

5. Accept/reject trades based on:
   - Personality thresholds
   - Current mood (anxiety lowers standards)
   - Trust in trading partner
   - Debt obligations (must pay debts first)
```

### 2. Possession System

**Mechanics:**
- Possess one kid at a time (3-5 second cooldown to switch)
- While possessed, you control that kid's actions
- Other kids continue autonomous behavior
- Possession drains a "Chaos Energy" meter slowly
- Breaking possession early refunds energy

**Possessed Actions:**
- Force unfavorable trades (give good candy for trash)
- Refuse good trades (creating frustration in others)
- Deliberately go into debt
- Hoard specific candy types
- Move to specific locations

**Possession UI:**
- Simple highlight around possessed kid (red glow)
- Minimal action buttons (Trade, Move, Borrow)
- Current kid's wallet display

### 3. Supply Manipulation System

**House Powers:**
- **Curse House**: Reduce quality/quantity from target house (30-60 seconds)
  - House gives out trash or lower-tier candy
  - Costs moderate chaos energy (15-20)
  - Creates artificial scarcity
  
- **Bless House**: Target house gives premium candy temporarily (30 seconds)
  - Attracts all nearby kids (creates hot spot)
  - Costs high chaos energy (25-30)
  - Can crash markets by flooding supply

**Strategic Uses:**
- Curse popular houses to create scarcity → drive up prices
- Bless houses right before possessed kid arrives (insider trading)
- Create supply shocks that trigger panic
- Control where kids congregate by blessing houses

**Implementation:**
- Activated by clicking on house while NOT possessed
- Visual effect: Glowing aura around house (red curse, green bless)
- Kids notice and adjust paths to avoid cursed/approach blessed houses

### 4. Rumor System

**Rumor Types:**
- **Price Rumors**: "Snickers are going to be worth 3x tomorrow!"
- **Quality Rumors**: "All Skittles from Oak Street are stale!"
- **Person Rumors**: "Jimmy is a scammer, don't trade with him!"
- **Event Rumors**: "Mrs. Henderson is giving out king-size bars!"

**Spread Mechanics:**
- Costs chaos energy (different amounts per rumor type)
- Target one kid or area
- Spreads via social networks (friends tell friends)
- Decays over time (20-60 seconds depending on believability)
- Mutates as it spreads (like telephone game)
- Effectiveness based on kid's trust level and current mood

**Rumor Effects:**
- Kids adjust believed values without checking real values
- Can create artificial scarcity (everyone avoids certain houses)
- Can trigger panic selling or buying
- Can isolate specific kids from trades

### 5. Cartel & Alliance System

**Trading Blocs:**
- Kids in same social network naturally form "trading blocs" over time
- Bloc members share believed values faster (information advantage)
- Trade preferentially with bloc members (lower standards, better rates)
- Blocs can dominate specific candy markets

**Bloc Formation:**
- Forms automatically when 3+ kids with strong friendship trade frequently
- Visual: Same-colored tint or icon above bloc members
- Bloc strength increases with successful trades between members
- Blocs can fracture due to betrayals or bad trades

**Player Manipulation:**
- Infiltrate blocs by possessing a member and breaking trust
- Create new blocs by spreading rumors that unite kids against others
- Exploit insider trading (bloc knows something market doesn't)
- Trigger bloc wars (two cartels compete for market dominance)

**Strategic Implications:**
- "Inside traders" have information advantage
- "Outside traders" get worse deals
- Natural faction warfare emerges
- Creates scenarios: "Destroy the Chocolate Cartel"

### 6. Price Discovery System

**Initial Phase (First 2-3 minutes):**
- Kids start with NO knowledge of candy values
- believed_values initialize randomly (0.5-5.0 for most candies)
- Wild West period: kids make terrible trades while learning
- Market gradually discovers "true" values through trading

**Discovery Mechanics:**
- Kids adjust believed_values based on:
  - Trades they make (if accepted, value was reasonable)
  - Trades they observe nearby
  - Rumors they hear (can mislead discovery)
- Convergence happens naturally over 2-4 minutes
- OR you can extend chaos by spreading conflicting rumors

**Strategic Exploitation:**
- Early game is a land grab (acquire premium candy cheap)
- Possess kids during confusion to make one-sided deals
- Spread rumors during discovery to permanently warp beliefs
- Prevent market stabilization for ongoing chaos

**Phases:**
- Phase 1 (0-2 min): Pure chaos, value discovery
- Phase 2 (2-5 min): Market stabilizing, patterns emerge
- Phase 3 (5+ min): Established market, harder to manipulate without powers

### 7. Behavior Contagion System

**Imitation Mechanics:**
- When kids observe nearby kids making profitable trades, they copy strategies
- "Monkey see, monkey do" behavior spreads through crowds
- Creates fads: "Everyone's hoarding Skittles because Jimmy got rich"

**Contagion Patterns:**
- Successful hoarder → Nearby kids become hoarders
- Profitable momentum trade → Others become momentum traders
- Kid gets scammed → Others become risk-averse

**Strategic Uses:**
- Possess a kid, execute profitable strategy → Watch it spread
- Create a successful trade pattern, then rug-pull
- Use one kid as a "patient zero" for behavior epidemic
- Counter enemy strategies by showing alternative works better

**Implementation:**
- Kids track success of nearby kids' strategies
- Gradually shift personality_type toward successful strategies
- Caps: Can't completely change (hoarder won't become panic seller)
- Time-limited: Effects fade if strategy stops working

### 8. Economy System

**Candy Types** (6-8 types):
- Chocolate (Snickers, M&Ms, Reese's)
- Fruity (Skittles, Starburst)
- Sour (Sour Patch, Warheads)
- Novelty (Ring Pops, Lollipops)
- Health (Fruit snacks, Pretzels)
- Trash (Raisins, Pennies)

**Value System:**
- **Real Value**: Objective baseline (1-10 scale)
- **Believed Value**: What kids think it's worth (influenced by rumors, trades, scarcity)
- **Market Price**: Emerges from actual trades happening

**Economic Mechanics:**

**Debt System:**
- Kids can borrow candy to make trades now
- Must repay within time limit or social credit drops
- Debt cascades: If Kid A owes Kid B, and Kid B owes Kid C, and A defaults, B may default to C
- You can trigger cascades by possessing debtors and refusing to pay

**Futures Contracts** (Advanced):
- Kids bet on future prices: "I'll give you 2 Snickers now for 5 M&Ms tomorrow"
- You can manipulate supply to make bets fail spectacularly
- Defaults cause mood changes and trust damage

**Decay System:**
- All candy slowly degrades quality over time (5-10 minutes)
- Creates urgency, prevents infinite hoarding
- Decayed candy loses value, eventually becomes trash
- Time pressure creates interesting trade timing decisions

**Mood-Based Pricing:**
- Happy kids: Pay fair value
- Anxious kids: Overpay for security candy
- Greedy kids: Underpay, try to scam
- You manipulate moods via rumors, trades, or events

### 9. Personal Goals & Motivations System

**Goal Types:**
Each kid has a personal goal that affects their trading:
- **Collector**: "Collect all 8 candy types" - Overpays for missing types
- **Romantic**: "Get 10 romantic candies (hearts, roses)" - Desperate for specific items
- **Competitor**: "Have most candy by end of night" - Hoards, rarely trades
- **Specialist**: "Get 20 of my favorite candy" - Single-minded focus
- **Social**: "Make 10 friends through trading" - Accepts bad trades to build relationships
- **Risk-Taker**: "Make biggest trade of the night" - Goes for high-stakes deals

**Goal Effects:**
- Influences trade evaluation (override normal logic for goal items)
- Visible in Kid Dossier once discovered
- Creates exploitable weaknesses
- Adds personality without complex AI

**Strategic Exploitation:**
- Identify goals through observation
- Possess kids to prevent goal completion (emotional damage)
- Exploit desperate kids who need goal items
- Create conflicts (two collectors want same rare candy)

### 10. Random Events System

**Event Types:**
- **Parent Patrol**: Random parent confiscates candy from kid (creates desperate trader)
  - Frequency: Every 3-5 minutes
  - Effect: Kid loses 30-50% of inventory, becomes anxious
  
- **Rain Storm**: All kids move toward shelter house (creates trading hotspot)
  - Duration: 30-45 seconds
  - Effect: High-density trading, rumors spread faster
  
- **Bully Appears**: NPC bully demands "protection candy" from kids
  - Target: 1-2 kids at random
  - Effect: Creates debt, fear mood, desperate trades
  
- **Mystery House Opens**: Late-game house opens with unknown candy type
  - Timing: After 5+ minutes
  - Effect: Market disruption, speculation, exploration rush
  
- **Candy Recall**: Rumor of contamination for one candy type
  - Target: Random candy type
  - Effect: Market crash for that candy, panic selling

**Event Cadence:**
- 2-4 events per scenario
- Timed randomly to prevent predictability
- Player can't control events (pure external chaos)
- Forces adaptation of strategies

**Strategic Impact:**
- Creates opportunities (desperate kid after confiscation)
- Disrupts plans (your hoard gets stolen)
- Adds replayability
- Tests player adaptability

### 11. Combo Recognition System

**Tracked Combos:**
- **Short Squeeze**: Spread rumor → Possess & hoard → Dump when price peaks
  - Bonus: +25 chaos energy
  - Requirements: Price rises 50%+, sell within 20 seconds of peak

- **Pump and Dump**: Possess momentum trader → Buy heavily → Spread positive rumor → Others pile in → Sell high
  - Bonus: +30 chaos energy
  - Requirements: 3+ other kids buy same candy, profit 100%+

- **Debt Bomb**: Create debt chain → Spread panic rumor → Trigger cascade
  - Bonus: +40 chaos energy
  - Requirements: Cascade affects 5+ kids

- **Market Maker**: Buy low from one kid, sell high to another within 10 seconds
  - Bonus: +15 chaos energy
  - Requirements: 50%+ profit margin

- **The Rug Pull**: Start profitable behavior → Let it spread → Counter when copied
  - Bonus: +35 chaos energy
  - Requirements: 3+ kids copy behavior, you profit from reversal

- **Supply Shock**: Curse house → Hoard that candy → Price spikes → Sell
  - Bonus: +20 chaos energy
  - Requirements: Price doubles, sell within 30 seconds

**Combo Feedback:**
- Toast notification: "COMBO: SHORT SQUEEZE! +25 Chaos"
- Visual effect (fireworks, screen flash)
- Combo log in pause menu showing discovered combos
- Achievements for discovering all combos

**Learning System:**
- First time combo triggered: Full explanation shown
- Subsequent triggers: Quick toast only
- Teaches depth through positive reinforcement
- Encourages experimentation

### 12. Progression & Unlocks

**Chaos Energy:**
- Primary resource for actions
- Regenerates slowly (or from causing economic disruption)
- Max capacity increases with progression

**Unlock Tree (Memory-Based):**
- **Tier 1** (Start): Possess, Basic Rumors, Observe
- **Tier 2** (Cause 10 bad trades): Advanced Rumors (Price manipulation), Curse House
- **Tier 3** (Cause market crash): Debt Triggers, Multi-possess (rapid switching), Bless House, Combo Detection
- **Tier 4** (Bankrupt 5 kids): Prophecy Hints (see future trends), Mood Manipulation, Supply Rumors, Cartel Manipulation
- **Tier 5** (Complete scenario): Rule Creation (set neighborhood laws), Advanced Combos, Event Influence

**Knowledge System:**
- Learn kid personalities by watching them trade
- Learn social networks by observing conversations
- Learn preferences by seeing what they keep vs trade
- Learn personal goals through observation and dossier
- Discover trading blocs and their members
- Unlocks "Kid Dossier" UI showing everything you've learned

### 13. Map & Movement

**Neighborhood Layout:**
- Grid-based or node-based neighborhood (15-25 houses)
- Kids move autonomously house to house
- Natural gathering points (street corners, popular houses)
- Trading happens when kids are adjacent/nearby

**Houses:**
- Dispense candy at intervals
- Different house quality (some give better candy)
- Can be affected by rumors (kids avoid/flock to)

**Zones:**
- Neighborhoods naturally form trading zones
- Zone effects: If everyone in a zone believes a rumor, it reinforces
- Peer pressure: Kids in same zone gradually align behaviors

---

## Game Modes / Scenarios

### 1. Tutorial: "First Halloween"
- Learn possession, trading, basic rumors, supply manipulation
- Goal: Cause 10 unfavorable trades
- 5 kids, simple preferences, no random events
- Price discovery enabled (teaches market dynamics)

### 2. Scenario: "Market Crash"
- Goal: Crash the chocolate market
- 15 kids, debt enabled, cartels form naturally
- Win: Chocolate value drops below 2 for 30 seconds
- Unlocks: Debt manipulation powers

### 3. Scenario: "The Monopolist"
- Goal: Make one kid own 80% of a candy type
- 20 kids, aggressive AI, personal goals active
- Win: Any kid achieves monopoly
- Unlocks: Advanced cartel manipulation

### 4. Scenario: "Debt Spiral"
- Goal: Trigger a cascade affecting 10+ kids
- 15 kids, all start with debt, random events enabled
- Win: Chain bankruptcy event
- Unlocks: Prophecy hints

### 5. Scenario: "Cartel Wars"
- Goal: Create two opposing trading blocs and make them war
- 25 kids, social networks strong, behavior contagion enabled
- Win: Two cartels each control 40%+ of market, trading bloc rivalry
- Unlocks: Event influence powers

### 6. Scenario: "Hostile Takeover" (Advanced)
- Goal: Use all combo strategies to hit chaos threshold
- 30 kids, all systems enabled, high difficulty
- Win: 500+ chaos points in 10 minutes
- Unlocks: Sandbox mode

### 7. Sandbox: "Free Market"
- No goals, just experiment
- All powers unlocked
- Adjustable parameters:
  - Kid count (5-40)
  - Starting wealth distribution
  - Event frequency
  - Price discovery speed
  - Cartel formation rate

---

## UI Design (Minimal)

### Main View
- Top-down 2D view of neighborhood
- Kids as simple sprites with icons indicating activity
- Houses as static sprites
- Candy icons floating above kids showing their inventory

### HUD Elements
- **Chaos Energy Bar** (top left)
- **Current Objective** (top center)
- **Possessed Kid Info** (bottom left): Name, Mood, Wallet (3-4 candy icons), Personal Goal
- **Market Ticker** (bottom right): Scrolling candy prices with ↑↓ indicators
- **Combo Notifications** (center): Toast-style popups for discovered combos

### Interaction Panels (Simple Popups)
- **Trade Window**: Two columns showing each kid's offer (drag-drop candy icons)
- **Rumor Menu**: List of 4-6 rumor templates with target selection, shows chaos cost
- **Kid Dossier**: Simple stat sheet (unlocked gradually) including:
  - Personality type
  - Personal goal
  - Trading bloc membership
  - Recent trades
  - Trust level
  - Mood history
- **Market Graph**: Line graph showing candy value over time (optional, advanced)
- **Combo Log**: List of discovered combos with bonuses

### Quick Stats Overlay (Hold TAB)
- **Richest Kid**: By total candy value
- **Biggest Hoarder**: Most of single candy type
- **Most Indebted**: Highest debt
- **Market Momentum**: Which candies are ↑↓
- **Active Cartels**: Current trading blocs
- **Next Event**: Countdown to next random event

This overlay appears as transparent text over the game view - no fancy graphics needed.

### Action Feedback
- **Chaos Score Breakdown**: Shows point values before actions
  - "Spread rumor: +5 chaos"
  - "Bad trade: +2 chaos"
  - "Debt cascade: +10 per kid"
  - "Combo bonus: +25 chaos"
- Helps players understand scoring and optimize strategies

### Visual Feedback
- Price changes: Numbers float up (green) or down (red) above kids
- Rumors: Speech bubble icon with color coding
- Trades: Brief animation of candy icons swapping
- Mood: Simple emoji above kid head
- Possession: Red glow/outline

### No Complex UI
- No inventory management screens
- No skill trees or complicated menus
- No crafting interfaces
- Everything observable from main view or simple popups

---

## Technical Architecture

### Core Classes

```python
class Kid:
    - id, position, personality_type
    - candy_inventory: dict[CandyType, int]
    - preferences: dict[CandyType, float]
    - believed_values: dict[CandyType, float]
    - mood: Mood enum
    - social_network: list[Kid]
    - debts: dict[Kid, dict[CandyType, int]]
    - memory: list[Event]
    - personal_goal: Goal (NEW)
    - trading_bloc: TradingBloc or None (NEW)
    - observed_strategies: dict[Strategy, success_rate] (NEW)
    - update() - AI tick
    - evaluate_trade() - Trade decision logic
    - hear_rumor() - Update beliefs
    - observe_trade() - Learn from others (NEW)
    - adjust_strategy() - Behavior contagion (NEW)

class Economy:
    - real_values: dict[CandyType, float]
    - market_history: list[(timestamp, CandyType, price)]
    - price_discovery_active: bool (NEW)
    - discovery_progress: float (NEW)
    - calculate_market_price() - Based on recent trades
    - apply_decay() - Reduce candy quality over time
    - update_price_discovery() - Gradual convergence (NEW)

class House:
    - position, candy_quality
    - candy_types: list[CandyType]
    - dispense_rate: float
    - curse_timer: float (NEW)
    - bless_timer: float (NEW)
    - quality_multiplier: float (NEW)
    - dispense_candy() - Give candy to kids
    - apply_curse() - Reduce quality (NEW)
    - apply_blessing() - Boost quality (NEW)

class TradingBloc:
    - members: list[Kid]
    - shared_beliefs: dict[CandyType, float]
    - bloc_strength: float
    - formation_time: float
    - update() - Synchronize beliefs
    - add_member() - Grow bloc
    - remove_member() - Shrink/fracture bloc
    - calculate_strength() - Based on successful trades

class PersonalGoal:
    - goal_type: GoalType enum
    - target_candy: CandyType or None
    - target_amount: int
    - progress: float
    - affects_trade_evaluation() - Modify kid's decisions

class RandomEvent:
    - event_type: EventType
    - target: Kid or House or Area
    - duration: float
    - trigger_time: float
    - execute() - Apply event effects
    - resolve() - Clean up after event

class ComboDetector:
    - tracked_actions: list[PlayerAction]
    - combo_definitions: dict[str, ComboPattern]
    - check_for_combos() - Pattern matching
    - award_combo() - Give bonus chaos energy

class Rumor:
    - type: RumorType
    - content: string
    - believability: float
    - origin_kid: Kid
    - spread_radius: int
    - age: float
    - spread() - Propagate to nearby kids
    - mutate() - Change as it spreads

class PossessionSystem:
    - current_target: Kid
    - chaos_energy: float
    - unlocked_powers: list[Power] (NEW)
    - possess(kid) - Take control
    - release() - Stop possession
    - execute_action() - Perform possessed action
    - curse_house() - Supply manipulation (NEW)
    - bless_house() - Supply manipulation (NEW)

class GameWorld:
    - kids: list[Kid]
    - houses: list[House]
    - economy: Economy
    - active_rumors: list[Rumor]
    - trading_blocs: list[TradingBloc] (NEW)
    - pending_events: list[RandomEvent] (NEW)
    - combo_detector: ComboDetector (NEW)
    - update() - Main game loop tick
    - spawn_random_event() - Event system (NEW)
    - update_cartels() - Bloc formation/management (NEW)
```

### Data Structures

**Save Data:**
- Unlocked powers
- Completed scenarios
- High scores (chaos caused, fastest crashes, etc.)

**Simple JSON configs:**
- Kid personality templates
- Candy type definitions
- Scenario objectives
- Rumor templates

### Performance Targets
- 20-30 kids running simultaneously
- 60 FPS with simple 2D rendering
- AI updates every 2-3 seconds (not every frame)
- Trade calculations: O(n²) acceptable with <30 kids

---

## Art Requirements (Minimal)

### Sprites Needed
- **Kids**: 6-8 simple character sprites (can recolor for variety)
  - Idle stance
  - Walking animation (4 frames optional, or just slide)
  - Maybe different costumes (pirate, witch, ghost)
  
- **Houses**: 3-4 house types (small, medium, large, spooky)
  - Static sprites, no animation needed

- **Candy Icons**: 6-8 simple candy icons (32x32 or 64x64)
  - Color-coded for easy recognition

- **UI Elements**: 
  - Simple buttons (Start, Possess, Rumor, etc.)
  - Energy bar graphic
  - Speech bubble for rumors
  - Emoji mood icons (5 types)

- **Effects**:
  - Particle effect for trades (candy icon flash)
  - Red glow shader for possession
  - Number pop-ups for price changes

### Sound (Optional, Simple)
- Background music (Halloween themed, looping)
- UI click sounds
- Trade "ding" sound
- Rumor spread "whisper" sound
- Chaos/evil laugh when causing crashes

---

## Scope Boundaries (What's NOT Included)

### Cut Features
- **No Breeding/Evolution**: Too complex for v1.0, too slow-paced
- **No Alchemy/Crafting**: Doesn't fit economy focus
- **No Building Placement**: Not needed for economy sim
- **No Complicated Combat**: Keep it economic warfare only
- **No Seasonal Progression**: Single Halloween night
- **No Real-Time Multiplayer**: Single-player only

### Potential Future Additions (Post-MVP)
- More scenario types
- Kid costume customization (cosmetic)
- Neighborhood editor
- Challenge modes (speed runs, restrictions)
- New rumor types
- More complex debt instruments

---

## Success Metrics

### Player Engagement
- Average session length: 15-30 minutes
- Scenario completion rate: >60%
- Replay scenarios with different strategies

### Emergent Behavior Goals
- Unpredictable market crashes from simple rules
- Players discover strategies not explicitly taught
- "War stories" - memorable economic chaos moments
- Each playthrough feels different

### Technical Goals
- Stable 60 FPS with 30 kids
- No game-breaking bugs in core trading logic
- Save/load works reliably
- Clean, maintainable code architecture

---

## Development Philosophy

### Backend Focus
- Invest time in robust AI and economy systems
- Trading logic should be bulletproof
- Rumor propagation should feel organic
- Emergence over scripted events

### UI Philosophy
- "Good enough" is good enough
- Clarity over beauty
- Information should be discoverable, not hidden
- Feedback loops must be obvious (action → consequence)

### Iteration Strategy
- Get basic possession + trading working first
- Add rumors once trading is solid
- Layer in debt and complexity gradually
- Playtest for emergent behavior at each stage

---

## Risk Assessment

### High Risk
- **AI Balancing**: Making kids smart enough but exploitable
  - Mitigation: Extensive testing, tunable parameters
  
- **Performance**: 30 AI agents running trading logic
  - Mitigation: Optimize AI ticks, spatial partitioning for trade checks

### Medium Risk
- **Player Confusion**: Indirect control might feel powerless
  - Mitigation: Clear feedback, tutorial, gradual unlock of powers
  
- **Runaway Economies**: Systems might stabilize too much or collapse too fast
  - Mitigation: Tunable economic parameters, decay system prevents stagnation

### Low Risk
- **Art Requirements**: Minimal sprites needed
- **Scope Creep**: Clear cut features list
- **Technical Feasibility**: All systems are proven mechanics in pygame

---

## Comparable Games (For Reference)

- **Reigns**: Simple input, complex consequences
- **SimAnt/SimLife**: Emergent behavior from simple rules  
- **Cart Life**: Economic simulation with minimal graphics
- **Luck be a Landlord**: Simple loop, deep strategy
- **Universal Paperclips**: Incremental complexity from simple start

---

## Unique Selling Points

1. **Halloween theme** rarely seen in economy sims
2. **Playing as a demon** - villain protagonist is fun
3. **Indirect control** creates puzzle-like optimization
4. **Emergent chaos** from deterministic rules
5. **Information warfare** as primary mechanic
6. **Low barrier to entry**, high skill ceiling

---

## Development Priorities

### Must Have (MVP)
- [ ] Autonomous kid movement and trading
- [ ] Possession system
- [ ] Basic rumor spreading
- [ ] 3-4 candy types with preferences
- [ ] Simple debt system
- [ ] 1 complete tutorial scenario
- [ ] Basic UI (HUD, trade window, rumor menu)

### Should Have (v1.0)
- [ ] 3-4 full scenarios
- [ ] Unlock progression system
- [ ] Kid dossier/knowledge system
- [ ] Market history visualization
- [ ] Decay system
- [ ] 6-8 candy types
- [ ] Save/load

### Nice to Have (Post-Launch)
- [ ] Sandbox mode
- [ ] More rumor types
- [ ] Futures contracts
- [ ] Mood manipulation powers
- [ ] More scenarios
- [ ] Sound effects and music

---

## Estimated Development Timeline

**Phase 1: Core Systems (4-6 weeks)**
- Week 1-2: Basic pygame setup, kid movement, simple map
- Week 3-4: Trading AI logic, economy system
- Week 5-6: Possession system, basic UI

**Phase 2: Depth (4-6 weeks)**
- Week 7-8: Rumor system and propagation
- Week 9-10: Debt system, decay mechanics
- Week 11-12: Polish trading AI, balance testing

**Phase 3: Content & Polish (3-4 weeks)**
- Week 13-14: Tutorial scenario, 2-3 main scenarios
- Week 15: Unlock progression, knowledge system
- Week 16: Bug fixes, performance optimization, juice/polish

**Total: 12-16 weeks (3-4 months)**

---

## Conclusion

"Candy Capitalism" leverages your backend strengths to create a unique economic manipulation game with minimal UI demands. The focus on emergent AI behavior, indirect control, supply-and-demand mastery, and information warfare creates incredible depth without requiring complex graphics or animations. 

The expanded systems (price discovery, cartels, behavior contagion, personal goals, combos, and random events) create a rich simulation where simple rules generate complex, unpredictable outcomes. The Halloween theme provides a fun, lighthearted wrapper around sophisticated economic simulation.

The game is scoped for solo development with clear boundaries and a strong core loop. The modular design allows features to be developed and tested incrementally, with each system adding meaningful depth to the player's strategic options. Post-launch, the game can be expanded with new scenarios, mechanics, and community-requested features.

**Key Differentiators:**
- Deep economic simulation meets accessible Halloween theme
- Villain protagonist with indirect control creates unique puzzle gameplay
- Combo system teaches depth through positive reinforcement
- Emergent cartels and factions without scripted faction systems
- Price discovery phase creates distinct early/mid/late game dynamics
- Behavior contagion makes every action potentially create ripple effects

The game is designed to reward mastery - surface-level play yields chaos, but skilled players can orchestrate precise economic warfare through understanding the interconnected systems.
