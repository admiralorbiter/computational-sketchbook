# Candy Capitalism - Sprint Breakdown

## Development Sprint Plan (9 Sprints × 2 Weeks = 18 Weeks)

---

## **SPRINT 0: Pre-Development Setup** (3-5 days)

### Goals
- Set up development environment
- Create project structure
- Establish core architecture
- Set up version control

### Deliverables
- [ ] Pygame project initialized
- [ ] Git repository with .gitignore
- [ ] Basic folder structure:
  ```
  /src
    /entities (Kid, House, Rumor classes)
    /systems (Economy, Possession, AI)
    /ui (HUD, menus, popups)
    /data (configs, sprites)
    /utils (helpers, constants)
  /assets
    /sprites
    /sounds (placeholder)
  /tests
  ```
- [ ] Requirements.txt with dependencies
- [ ] Constants file (screen size, colors, game settings)
- [ ] Main game loop skeleton

### Technical Tasks
1. Install pygame, set up virtual environment
2. Create game window with 60 FPS loop
3. Set up sprite groups and basic rendering
4. Create base Entity class
5. Set up simple config loading (JSON)

### Success Criteria
- Game window opens and runs at 60 FPS
- Can load and display test sprite
- Project is version controlled

---

## **SPRINT 1: Core World & Movement** ✅ COMPLETED (Weeks 1-2)

### Goals
- Create neighborhood map
- Implement kid entities with autonomous movement
- Basic rendering and camera

### Deliverables
- [x] Grid-based neighborhood (15-20 houses)
- [x] House entities that spawn candy periodically
- [x] Kid entities that move autonomously
- [x] Simple pathfinding (A* or waypoint-based)
- [x] Top-down camera view
- [x] Basic sprite rendering

### Polish Features Added
- [x] Particle effects for candy dispensing
- [x] House cooldown visualization with progress bars
- [x] Inventory UI with candy breakdown (toggle with 'I' key)
- [x] Personality indicators on kids
- [x] Kid collision detection and separation
- [x] Enhanced debug overlay with comprehensive information
- [x] Camera controls (arrow keys, zoom, mouse wheel)
- [x] Help overlay (toggle with 'H' key)

### Technical Tasks
1. **World System**
   - Create Map class with grid or node structure
   - Implement House class with position and candy_quality
   - Generate neighborhood layout programmatically or from config

2. **Kid Movement**
   - Create Kid class with position, velocity, target
   - Implement simple pathfinding to move between houses
   - Add collision detection (kids don't overlap houses)
   - Kids autonomously pick next house destination

3. **Rendering**
   - Camera system (can be fixed or follow mouse)
   - Sprite manager for rendering all entities
   - Z-ordering (houses behind kids)
   - Debug mode (show paths, zones, hitboxes)

4. **Art (Placeholder OK)**
   - Simple house sprites (3 types)
   - Simple kid sprite (can be colored squares initially)
   - Tile/background texture

### Success Criteria
- [x] 10 kids move around neighborhood automatically
- [x] Kids pathfind to houses and "trick-or-treat"
- [x] Runs at 60 FPS with 10+ kids
- [x] Can visually distinguish kids and houses

### Additional Achievements
- [x] 178 tests passing (100% pass rate)
- [x] Particle effects for visual feedback
- [x] House cooldown system preventing spam
- [x] Kid collision detection and separation
- [x] Inventory UI with candy breakdown
- [x] Personality indicators on kids
- [x] Comprehensive debug and help overlays

### Testing Focus
- Pathfinding doesn't break with obstacles
- Kids don't get stuck
- Performance with 20+ kids

---

## **SPRINT 2: Core Trading System** ✅ COMPLETED (Weeks 3-4)

### Goals
- Implement candy inventory system
- Create trading AI logic
- Kids autonomously initiate and complete trades

### Deliverables
- [x] Candy type definitions (6-8 types)
- [x] Inventory system for kids
- [x] Trade proposal and acceptance logic
- [x] Trading AI that evaluates trades based on preferences
- [x] Visual feedback for trades happening
- [x] Price discovery system (kids start with random beliefs)

### Technical Tasks
1. **Candy System**
   - Create CandyType enum/class
   - Define real_values and properties (decay rate, etc.)
   - Create Inventory class (dict of candy types to counts)

2. **Economy Class**
   - Track real values for all candy types
   - Calculate market prices from recent trades
   - Store trade history
   - Method to update market prices
   - **Price Discovery**: Initialize believed_values randomly (0.5-5.0)
   - **Convergence Logic**: Kids gradually learn true values through trading

3. **Trading Logic**
   - Kid preferences (random generation for now)
   - Trade evaluation function:
     ```python
     def evaluate_trade(self, offer_candy, request_candy):
         # Calculate value delta based on preferences AND believed values
         # Return acceptance probability
     ```
   - Trade proposal system (kids scan nearby kids)
   - Trade acceptance based on personality (simple for now)
   - **Learning**: Update believed_values after each trade

4. **Kid AI - Trading Behavior**
   - Every 3 seconds, check nearby kids
   - Evaluate potential trades using believed_values (not real_values)
   - Propose trades if beneficial
   - Accept/reject incoming proposals
   - Execute trade (swap inventories)
   - **Adjust beliefs** after trades (move toward equilibrium)

5. **Visual Feedback**
   - Candy icons float above kids
   - Trade animation (icons swap between kids)
   - Sound effect placeholder
   - **Price discovery indicator**: Show convergence progress (optional)

### Success Criteria
- [x] Kids autonomously propose and complete trades
- [x] Trading follows logical preference rules
- [x] Can observe 5+ trades per minute with 10 kids
- [x] Market prices reflect actual trades
- [x] **Believed values converge toward real values over 2-3 minutes**
- [x] **Early game feels chaotic, late game more stable**

### Additional Features Implemented
- [x] Multi-item trades (1-3 candy types per trade)
- [x] Economy system with real values and market prices
- [x] Configurable price discovery modes (fixed/random/convergent)
- [x] Trade visualization with particles and floating text
- [x] Market ticker showing real-time prices
- [x] Economy debug overlay (press 'E' key)
- [x] Enhanced inventory display with value information
- [x] 12 comprehensive unit tests for trading logic

### Testing Focus
- Trade logic is fair (no exploits)
- Kids don't deadlock in trade negotiations
- Economy doesn't break (no negative candy, etc.)

---

## **SPRINT 3: Possession System & Basic UI** (Weeks 5-6)

### Goals
- Implement player possession mechanic
- Create basic HUD and interaction UI
- Player can force bad trades

### Deliverables
- [ ] Chaos Energy system
- [ ] Possess/release mechanics
- [ ] Player-controlled trading while possessed
- [ ] Basic HUD (energy bar, possessed kid info)
- [ ] Trade UI window
- [ ] Supply manipulation powers (Curse/Bless House)

### Technical Tasks
1. **Possession System Class**
   - Track current possessed kid
   - Chaos energy pool (max 100, regenerates 1/sec)
   - Possess costs energy, drains slowly while active
   - Cooldown system (3-5 seconds between switches)

2. **Player Input Handling**
   - Click to possess kid
   - ESC to release possession
   - WASD or arrows to move possessed kid
   - Spacebar or click to initiate trade
   - **Click on house (while not possessed) to curse/bless**

3. **Supply Manipulation**
   - Add quality_multiplier to House class
   - **Curse House** power:
     - Costs 15-20 chaos energy
     - Reduce house quality_multiplier to 0.3-0.5 for 30-60 seconds
     - House gives trash candy or very low quality
     - Visual: Red glow around house
   - **Bless House** power:
     - Costs 25-30 chaos energy
     - Boost quality_multiplier to 2.0-3.0 for 30 seconds
     - House gives premium candy
     - Attracts nearby kids (pathfinding weight)
     - Visual: Green/gold glow around house

4. **Trade UI Window**
   - Simple popup showing both kids' inventories
   - Drag-drop or click interface to build trades
   - Confirm/cancel buttons
   - Shows trade value delta
   - **Shows chaos energy gained from bad trades**

5. **HUD Elements**
   - Energy bar (top left) with recharge rate indicator
   - Possessed kid highlight (red glow sprite overlay)
   - Possessed kid info panel (name, mood, inventory summary, **personal goal**)
   - Simple objective text (top center)
   - **Chaos score with recent gains** (+2, +5 popups)

6. **Player Actions**
   - While possessed, player can:
     - Manually propose trades (bypass AI logic)
     - Accept/reject any incoming trade
     - Move to specific location
     - Force bad trades the AI wouldn't accept
   - **While not possessed**:
     - Click houses to curse/bless
     - Observe and plan next move

### Success Criteria
- Can possess any kid with mouse click
- Possession drains energy appropriately
- Can force a bad trade (give chocolate, get trash)
- **Can curse a house and observe kids avoid it**
- **Can bless a house and see kids flock to it**
- **Supply manipulation creates price changes**
- HUD clearly shows possession state
- Trade UI is functional (even if ugly)

### Testing Focus
- Possession switching is responsive
- Trade UI doesn't break game logic
- Can't exploit energy system

---

## **SPRINT 4: Rumor System** (Weeks 7-8)

### Goals
- Implement rumor spreading mechanic
- Rumors affect kid beliefs and behavior
- Visual feedback for rumor propagation

### Deliverables
- [ ] Rumor class and types
- [ ] Rumor spreading algorithm
- [ ] Kids adjust believed_values based on rumors
- [ ] UI for spreading rumors
- [ ] Visual feedback (speech bubbles, belief changes)
- [ ] Combo detection and recognition system

### Technical Tasks
1. **Rumor Class**
   - Properties: type, content, believability, age, spread_radius
   - Types: Price Rumor, Quality Rumor, Person Rumor, **Supply Rumor**
   - Method: spread() - propagates to nearby kids
   - Method: mutate() - changes content slightly
   - Method: decay() - reduces effectiveness over time

2. **Rumor Propagation**
   - When rumor created, affects target kid
   - Spreads through social network (friends tell friends)
   - Radius-based spreading (nearby kids overhear)
   - Mutation: rumor changes slightly each hop
   - Decay: rumors fade after 30-60 seconds

3. **Belief System**
   - Kids have believed_values separate from real_values
   - hear_rumor() method updates beliefs:
     ```python
     def hear_rumor(self, rumor):
         if rumor.type == "PRICE":
             believed_value *= rumor.modifier
             believed_value = clamp(0.1, 10.0)
     ```
   - Trading AI uses believed_values instead of real_values

4. **Rumor UI**
   - Radial menu or simple button menu
   - Select rumor type and target
   - **Shows chaos energy cost (5-15 depending on type)**
   - Shows preview of rumor text
   - **Shows potential combo opportunities**

5. **Combo Detection System**
   - ComboDetector class tracks player actions
   - Define combo patterns:
     - **Short Squeeze**: Rumor → Hoard → Price rise → Sell
     - **Pump and Dump**: Possess → Buy → Rumor → Others buy → Sell
     - **Supply Shock**: Curse house → Hoard → Price spike → Sell
   - Pattern matching after each player action
   - Award bonus chaos energy when combo triggered
   - Track discovered combos per session

6. **Combo Feedback**
   - Toast notification when combo triggered
   - "COMBO: SHORT SQUEEZE! +25 Chaos Energy"
   - Visual effect (screen flash, particle burst)
   - First-time discovery shows full explanation
   - Subsequent discoveries show quick toast
   - Combo log accessible in pause menu

7. **Visual Feedback**
   - Speech bubble icon appears over affected kids
   - Color-coded by rumor type
   - Shows rumor spread with particle effects
   - Price changes show as floating text
   - **Combo notifications prominent but not obtrusive**

### Success Criteria
- Can spread rumor to specific kid
- Rumor propagates to 3+ nearby kids
- Kids trade based on false beliefs (buy overpriced candy)
- Can observe panic behavior after bad rumor
- **Can execute Short Squeeze combo and see notification**
- **Combo system teaches player advanced strategies**
- **Chaos score visibly increases from combos**

### Testing Focus
- Rumor spreading doesn't cause infinite loops
- Beliefs eventually return to reality
- System doesn't become too chaotic (balance)

---

## **SPRINT 5: Debt & Mood Systems** (Weeks 9-10)

### Goals
- Implement borrowing and debt
- Add mood system affecting trade behavior
- Create debt cascade mechanics

### Deliverables
- [ ] Kids can borrow candy from each other
- [ ] Debt tracking and repayment
- [ ] Mood system (happy, anxious, greedy, panic)
- [ ] Debt cascades when defaults happen
- [ ] Moods affect trading behavior
- [ ] Personal goals system for kids

### Technical Tasks
1. **Debt System**
   - Add debts dict to Kid class
   - Borrow method: Kid A asks Kid B for candy, promises repayment
   - Repayment timer (60-120 seconds)
   - Default triggers mood change and social penalty
   - Debt cascade detection: if B owes C and A defaults to B...

2. **Mood System**
   - Enum: HAPPY, NEUTRAL, ANXIOUS, GREEDY, PANIC
   - Mood affects trade evaluations:
     - ANXIOUS: Accept worse trades for comfort candy
     - GREEDY: Only accept very favorable trades
     - PANIC: Sell everything at any price
   - Mood changes from events:
     - Good trade → HAPPY
     - Bad trade → ANXIOUS
     - Debt default → PANIC
     - Successful repayment → NEUTRAL

3. **Personal Goals System**
   - PersonalGoal class with types:
     - COLLECTOR: "Collect all 8 candy types"
     - ROMANTIC: "Get 10 romantic candies"
     - COMPETITOR: "Have most candy by night end"
     - SPECIALIST: "Get 20 of favorite candy"
     - SOCIAL: "Make 10 friends through trading"
     - RISK_TAKER: "Make biggest trade of night"
   - Each kid assigned random goal at start
   - Goals affect trade evaluation (override normal logic for goal items)
   - Progress tracking for each goal
   - **Goal completion gives kid satisfaction (mood boost)**

4. **AI Enhancements**
   - Include mood in trade evaluation
   - Include personal goal in trade evaluation
   - Prioritize debt repayment over new trades
   - Cascade detection: if a debtor defaults, creditor may default too
   - **Kids pursuing goals make irrational trades** (exploitable)

5. **Visual Feedback**
   - Emoji mood icon above kid
   - Debt indicator (red exclamation mark)
   - Cascade animation (domino effect)
   - **Goal icon/text in kid dossier**
   - **Progress bar for goals (when viewing dossier)**

6. **Kid Dossier Enhancement**
   - Add personal goal display
   - Add goal progress
   - Add goal-influenced recent trades
   - Highlight which kids are desperate for goal items

### Success Criteria
- Kids borrow and repay debts naturally
- Can trigger debt cascade by possessing debtor and refusing to pay
- Moods visibly affect behavior (panic sellers dump candy cheap)
- Cascade affects 3+ kids in chain reaction
- **Can identify and exploit kids pursuing goals**
- **Kids pursuing Collector goal overpay for missing types**
- **Goal system adds personality without complex AI**

### Testing Focus
- Debt logic doesn't break (no infinite debt)
- Cascades don't freeze game
- Moods reset appropriately

---

## **SPRINT 6: Cartels, Behavior Contagion & Personality Polish** (Weeks 11-12)

### Goals
- Implement candy decay system
- Polish AI with distinct personality types
- Add trading bloc/cartel formation
- Implement behavior contagion system
- Major balancing pass

### Deliverables
- [ ] Candy degrades over time
- [ ] 5 distinct kid personality types
- [ ] Balanced trading AI that feels natural
- [ ] Trading bloc formation and management
- [ ] Behavior contagion (kids copy successful strategies)
- [ ] Performance optimizations

### Technical Tasks
1. **Decay System**
   - Candy has freshness value (100% → 0%)
   - Decays over 5-10 minutes
   - Affects value in trades
   - Eventually becomes "trash" candy
   - Forces kids to trade before expiry

2. **Personality Types**
   - **Value Investor**: Waits for good deals, patient
   - **Momentum Trader**: Follows market trends, buys rising candies
   - **Hoarder**: Accumulates favorites, rarely trades
   - **Social Trader**: Trades with friends even at bad rates
   - **Panic Seller**: Sells quickly, easily influenced by rumors
   - Each has unique trade evaluation logic

3. **Trading Bloc System**
   - TradingBloc class tracks members and shared beliefs
   - Formation: 3+ kids with strong friendship trade frequently
   - Bloc members:
     - Share believed_values faster (info advantage)
     - Trade preferentially with each other
     - Get better rates within bloc
     - Display same-colored tint or icon
   - Bloc strength increases with successful internal trades
   - Blocs can fracture from betrayals or bad trades

4. **Cartel Mechanics**
   - Blocs naturally emerge from social networks
   - Can dominate specific candy markets
   - "Inside traders" vs "outside traders" dynamics
   - Bloc rivalries emerge when interests conflict
   - Visual: Same-colored outline for bloc members

5. **Behavior Contagion System**
   - Kids track success of nearby kids' strategies
   - observed_strategies dict tracks what works
   - When kid sees neighbor profit from strategy, copy it:
     ```python
     def observe_trade(self, other_kid, profit):
         if profit > threshold:
             self.observed_strategies[other_kid.strategy] += 1
             if count > 3:
                 shift_toward_strategy()
     ```
   - Creates behavioral waves/fads
   - Examples:
     - Successful hoarder → Others become hoarders
     - Profitable rumor trade → Others seek rumors
   - Caps: Can't completely change personality
   - Effects fade if strategy stops working

6. **AI Polish**
   - Tune trade frequency (not too fast, not too slow)
   - Balance risk tolerance per personality
   - Improve pathfinding efficiency
   - Add variety to movement patterns
   - **Make cartels visible and understandable**
   - **Contagion creates visible waves of behavior**

7. **Performance**
   - Profile game with 30 kids
   - Optimize trade checking (spatial partitioning)
   - Cache expensive calculations
   - Reduce unnecessary AI ticks
   - Optimize cartel update logic

8. **Balancing**
   - Tune chaos energy costs
   - Balance rumor effectiveness
   - Adjust debt timers
   - Tune candy values and preferences
   - **Balance cartel formation rate**
   - **Balance behavior contagion speed**
   - Test for edge cases and exploits

### Success Criteria
- Can see distinct personality behaviors
- Decay creates urgency in trading
- Game runs smooth with 25+ kids
- Economy feels dynamic but not random
- **Trading blocs form naturally within 3-4 minutes**
- **Can observe 2-3 distinct cartels competing**
- **Behavior contagion creates visible fads**
- **Can infiltrate cartel by possessing member**
- **"Destroy the Chocolate Cartel" is a viable strategy**

### Testing Focus
- Extensive playtesting
- Balance different strategies
- Check for dominant strategies

---

## **SPRINT 7: Scenarios, Random Events & Progression** (Weeks 13-14)

### Goals
- Create tutorial scenario
- Build 3-4 main scenarios with objectives
- Implement unlock/progression system
- Knowledge/learning system
- Random events system

### Deliverables
- [ ] Tutorial scenario (5-10 minutes)
- [ ] 3-4 full scenarios with win conditions
- [ ] Unlock tree for powers
- [ ] Kid dossier/knowledge system
- [ ] Scenario selection menu
- [ ] Random events system

### Technical Tasks
1. **Scenario System**
   - Scenario class with:
     - Kid count and types
     - Starting conditions
     - Win/lose conditions
     - Unlocked powers
     - Event frequency settings
   - Objective tracking system
   - Victory/defeat detection

2. **Tutorial Scenario**
   - Guided steps with on-screen prompts
   - Objective: Cause 10 bad trades, execute 1 combo
   - 5 kids, simple AI, no random events
   - Introduces possession, trading, rumors, supply manipulation one at a time
   - Shows first combo opportunity clearly

3. **Main Scenarios**
   - **"Market Crash"**: Crash chocolate market value
   - **"The Monopolist"**: One kid owns 80% of a candy type
   - **"Debt Spiral"**: Trigger 10+ kid cascade
   - **"Cartel Wars"**: Create two opposing trading blocs (NEW)
   - Each has different starting economies and kid configurations

4. **Random Events System**
   - RandomEvent class with types:
     - **Parent Patrol**: Confiscate candy (every 3-5 min)
     - **Rain Storm**: Kids shelter, trading hotspot (30-45 sec)
     - **Bully Appears**: Demands protection candy
     - **Mystery House**: New house with rare candy
     - **Candy Recall**: Contamination rumor tanks market
   - Event spawner with configurable frequency
   - 2-4 events per scenario at random times
   - Visual/audio cues for events
   - Events can't be controlled by player (pure chaos)

5. **Event Implementation**
   - Timer-based event spawner
   - Event execute() applies effects
   - Event resolve() cleans up
   - Each event type has unique logic:
     ```python
     class ParentPatrolEvent:
         def execute(self):
             target_kid = random.choice(kids)
             target_kid.lose_candy(30-50%)
             target_kid.mood = ANXIOUS
     ```

6. **Progression System**
   - Track "chaos points" earned
   - Unlock new powers:
     - Tier 1: Basic rumors, possess
     - Tier 2: Advanced rumors, curse house, faster possession
     - Tier 3: Debt manipulation, bless house, mood control, combo detection
     - Tier 4: Supply rumors, cartel manipulation, event hints
   - Save/load progress
   - Persistent unlock state

7. **Knowledge System**
   - Kid dossier UI
   - Gradually reveal info as you observe:
     - Personality type (after 5 trades observed)
     - Preferences (after 3 trades)
     - Personal goal (after observing goal-driven trade)
     - Social network (after observing conversations)
     - Trading bloc membership (when bloc forms)
   - "???" for unknown info
   - Info persists across possessions

8. **Quick Stats Overlay (Hold TAB)**
   - Richest kid (by total value)
   - Biggest hoarder
   - Most indebted
   - Market momentum (↑↓ indicators)
   - Active cartels
   - Next random event countdown
   - Simple text overlay, no fancy graphics

### Success Criteria
- Tutorial teaches core mechanics clearly
- Each scenario feels distinct
- Can complete all scenarios with different strategies
- Progression feels rewarding
- **Random events create unexpected opportunities/challenges**
- **Can see next event coming (adds tension)**
- **Quick Stats overlay helps track macro trends**
- **Events force player to adapt strategies**

### Testing Focus
- Tutorial is clear to new players
- Scenarios are beatable but challenging
- Progression curve feels right

---

## **SPRINT 8: Polish, Juice & Launch Prep** (Weeks 15-16)

### Goals
- Visual polish and game feel
- Menu systems
- Bug fixing and optimization
- Prepare for release

### Deliverables
- [ ] Main menu, pause menu, options
- [ ] Visual effects and animations
- [ ] Sound effects (if time permits)
- [ ] Final art pass (or finalize placeholder art)
- [ ] Save/load system
- [ ] Bug fixes from playtesting
- [ ] README and documentation

### Technical Tasks
1. **Menu Systems**
   - Main menu (New Game, Continue, Options, Quit)
   - Scenario select screen with unlock indicators
   - Pause menu
   - Victory/defeat screens with score breakdown
   - Options (volume, maybe difficulty sliders)
   - Combo log viewer

2. **Visual Polish**
   - Particle effects for trades
   - Screen shake for big events (cascades, combos)
   - Smooth camera transitions
   - Animated UI elements
   - Better kid walking animations (if time)
   - Polish possession glow effect
   - **Cartel member visual indicators (colored outlines)**
   - **Behavior wave visualization (when contagion spreads)**
   - **Event effects (rain, parent patrol, etc.)**

3. **Audio**
   - Background music (1-2 Halloween-themed loops)
   - Trade sound effect
   - Rumor spread sound (whisper)
   - Possession sound (demonic laugh)
   - Combo sound (satisfying chime)
   - Cascade/crash sound
   - House curse/bless sounds
   - UI click sounds
   - Event-specific sounds

4. **Game Feel (Juice)**
   - Floating damage numbers for price changes
   - Satisfying feedback for successful manipulation
   - Celebration particles when causing chaos
   - Smooth transitions between scenes
   - **Combo effects feel GREAT (screen flash, particles, sound)**
   - **Cascade domino effect with staggered timing**
   - **Supply shock visual wave**

5. **Final Art**
   - Replace placeholder sprites with final art
   - Create candy icons (8 types, distinct and recognizable)
   - Polish UI graphics
   - Title screen art
   - Victory/defeat screen art
   - **Cartel color schemes**
   - **Event icons**

6. **Save System**
   - Save progression data (unlocks, completed scenarios, high scores)
   - Load save on startup
   - JSON-based save file
   - Multiple save slots (optional)

7. **Bug Fixing**
   - Fix all critical bugs
   - Address performance issues
   - Polish edge cases
   - Improve error handling
   - **Test all combo patterns**
   - **Test cartel formation/fracture**
   - **Test random events don't break game state**

8. **Documentation**
   - In-game help/controls screen
   - README with setup instructions
   - Known issues list
   - **Combo guide (optional unlock)**
   - **Strategy tips document**

### Success Criteria
- Game feels polished and complete
- No game-breaking bugs
- Menus are functional and clear
- Save/load works reliably
- Art is cohesive (doesn't need to be AAA)
- **All systems feel interconnected and rewarding**
- **Combos feel satisfying to execute**
- **Visual feedback makes systems understandable**

### Testing Focus
- Full playthrough of all scenarios
- Check all edge cases
- Performance testing
- UX testing with fresh eyes

---

## **SPRINT 9: Sandbox Mode & Advanced Features** (Weeks 17-18)

### Goals
- Implement full sandbox mode with customization
- Add advanced optional features
- Final balance pass
- Prepare marketing materials

### Deliverables
- [ ] Sandbox mode with parameter sliders
- [ ] Advanced combo patterns
- [ ] Optional: Futures contracts
- [ ] Highscore tracking and leaderboards (local)
- [ ] Achievement system (optional)
- [ ] Trailer/screenshots for marketing

### Technical Tasks
1. **Sandbox Mode**
   - "Free Market" sandbox with all powers unlocked
   - Parameter sliders:
     - Kid count (5-40)
     - Starting wealth distribution (equal, random, skewed)
     - Event frequency (none, low, medium, high)
     - Price discovery speed (instant, slow, normal, never)
     - Cartel formation rate
     - Decay rate
     - Chaos energy regen rate
   - Save/load sandbox configurations
   - No objectives, pure experimentation
   - Timer display showing session length

2. **Advanced Combo Patterns**
   - **The Rug Pull**: Start profitable behavior → Let spread → Counter
   - **Market Maker**: Buy low, sell high within 10 seconds
   - **Triple Manipulation**: Possess + Rumor + Supply in sequence
   - **Cascade Chain**: Trigger 3+ cascades in row
   - Each combo has unique achievement

3. **Futures Contracts** (Optional Advanced Feature)
   - Kids can make future price bets
   - "I'll give you 2 Snickers now for 5 M&Ms in 60 seconds"
   - You manipulate supply to make bets fail
   - Adds gambling layer for advanced players
   - Only in sandbox or advanced scenarios

4. **Highscore System**
   - Track per-scenario high scores:
     - Fastest completion
     - Highest chaos generated
     - Most combos executed
     - Biggest cascade triggered
   - Local leaderboard display
   - Compare to your previous runs

5. **Achievement System** (Optional)
   - Track meta achievements:
     - "First Combo"
     - "Cartel Destroyer" - Break 10 cartels
     - "Debt Lord" - Trigger 50 cascades
     - "Supply Manipulator" - Curse/bless 100 houses
     - "Perfect Storm" - All 5 combo types in one scenario
   - Simple unlock notifications
   - Displayed in pause menu

6. **Marketing Materials**
   - Capture gameplay footage
   - Create 5-10 compelling screenshots
   - Write feature list
   - Create GIF of cool combo
   - Polish title screen for first impression

7. **Final Balance Pass**
   - Test all scenarios for difficulty curve
   - Ensure each system is useful (not too weak/strong)
   - Verify combo bonuses feel right
   - Check energy costs are balanced
   - Test sandbox doesn't have dominant strategy

8. **Documentation Polish**
   - Update README with final features
   - Create strategy guide
   - Document all combos
   - Explain each system clearly
   - Add troubleshooting section

### Success Criteria
- Sandbox mode is endlessly replayable
- Advanced features add depth without complexity
- All systems feel balanced
- Marketing materials are compelling
- Game is ready for release/distribution
- High scores motivate replay
- Achievement system adds long-term goals (if included)

### Testing Focus
- Extended sandbox sessions (30+ minutes)
- Test all parameter combinations
- Verify no gamebreaking combos
- Final external playtesting

---

## Post-Sprint: Potential Future Updates

### Update 1.1: Community Features
- Online leaderboards
- Share sandbox configurations
- Replay system for cool runs

### Update 1.2: More Content
- 3-5 new scenarios
- New random event types
- New candy types
- Holiday themes (Christmas, Easter)

### Update 1.3: Advanced Economics
- Stock market mechanics
- Insurance system
- Candy futures trading (if not in v1.0)
- Regulatory mechanics (player sets market rules)

### Update 1.4: Meta Progression
- Permanent unlocks across all runs
- Prestige system
- Challenge modes with modifiers
- Daily challenges

---

## Sprint Velocity & Adjustments

### Expected Velocity
- **Solo developer**: Roughly 40-60 hours per 2-week sprint
- **Assumes**: 20-30 hours/week development time
- **Buffer**: Each sprint has stretch goals vs core goals

### Adjust If Needed
- **Running ahead?** Add stretch features from "Nice to Have" list
- **Running behind?** Cut decay system or advanced personality types
- **Major blocker?** Pivot sprint focus, keep moving forward

### Critical Path
Must complete in order:
1. Sprint 1 (Movement) → Sprint 2 (Trading)
2. Sprint 2 → Sprint 3 (Possession)
3. Sprint 3 → Sprint 4 (Rumors)

Can parallelize:
- Art creation can happen alongside any sprint
- Audio can be added in Sprint 8 or post-launch

---

## Definition of Done (Per Sprint)

Each sprint is "done" when:
- [ ] All core deliverables implemented
- [ ] Code is committed to version control
- [ ] Basic testing completed (no critical bugs)
- [ ] Playable build runs without crashes
- [ ] Sprint retrospective documented (what worked, what didn't)

---

## Testing Strategy

### Per Sprint
- **Unit tests** for critical systems (economy calculations, AI logic)
- **Integration tests** for key flows (trading, debt cascades)
- **Playtest** at end of each sprint (15-30 min session)

### Mid-Project (After Sprint 4)
- Bring in external playtester
- Validate core loop is fun
- Major pivots if needed

### Final Testing (Sprint 8)
- Full playthrough by multiple testers
- Fix all critical bugs
- Polish based on feedback

---

## Risk Mitigation Per Sprint

### Sprint 1-2: Core Systems Risk
- **Risk**: Trading AI too complex/buggy
- **Mitigation**: Start simple, add complexity gradually
- **Fallback**: Use even simpler AI (random trades) initially

### Sprint 4: Rumor System Risk
- **Risk**: Rumors too powerful or too weak
- **Mitigation**: Make parameters easily tunable
- **Fallback**: Reduce rumor types if implementation takes too long

### Sprint 5: Debt Cascade Risk
- **Risk**: Cascades cause game instability
- **Mitigation**: Extensive edge case testing, cap cascade depth
- **Fallback**: Simplify cascade rules

### Sprint 7: Scenarios Risk
- **Risk**: Scenarios aren't fun or too hard/easy
- **Mitigation**: Playtest early, iterate on objectives
- **Fallback**: Ship with fewer scenarios, add more post-launch

---

## Success Metrics (End of Development)

### Technical
- [ ] Game runs at 60 FPS with 30+ kids
- [ ] Zero critical bugs
- [ ] Save/load works reliably
- [ ] Code is modular and maintainable
- [ ] All systems interact smoothly (no conflicts)

### Gameplay
- [ ] Tutorial completion rate >80%
- [ ] Average session length 20+ minutes
- [ ] Players discover unintended strategies
- [ ] "Aha!" moments when economy collapses
- [ ] **Combos feel satisfying to discover and execute**
- [ ] **Cartels emerge naturally and create drama**
- [ ] **Each scenario requires different strategy**

### Polish
- [ ] Consistent art style
- [ ] Clear UI feedback
- [ ] Satisfying game feel
- [ ] No confusion about what to do
- [ ] **Visual effects make systems understandable**
- [ ] **Audio reinforces actions**

---

## Sprint Planning Tips

### Weekly Routine
- **Monday**: Review last week, plan this week's tasks
- **Wednesday**: Mid-sprint check-in, adjust if needed
- **Friday**: Commit working build, playtest, retrospective

### Task Breakdown
- Break each deliverable into 2-4 hour tasks
- Track in simple tool (Trello, Notion, or text file)
- Focus on one task at a time

### Avoid Scope Creep
- Write down "cool ideas" for post-launch
- Stay focused on current sprint goals
- Only add features if ahead of schedule

### Playtest Every Sprint
- Even incomplete features
- Feels different playing vs watching code run
- Catch UX issues early

---

## Conclusion

This sprint plan takes the enhanced GDD and breaks it into actionable 2-week chunks over 18 weeks (4.5 months). The plan prioritizes getting a playable core loop quickly (Sprints 1-4), then adds depth systems (Sprints 5-6), content and progression (Sprint 7), polish (Sprint 8), and sandbox/advanced features (Sprint 9).

**Key Development Principles:**
- **Systems First**: Core economic simulation must be rock solid
- **Incremental Complexity**: Each sprint builds on previous work
- **Playtest Early**: Test emergent behavior at each stage
- **Flexible Scope**: Can ship after Sprint 8 if needed, Sprint 9 is polish

**Critical Path:**
1. Movement + Trading (Sprints 1-2) - Foundation
2. Possession + Supply Manipulation (Sprint 3) - Player agency
3. Rumors + Combos (Sprint 4) - Depth
4. Debt + Goals + Moods (Sprint 5) - Personality
5. Cartels + Contagion (Sprint 6) - Emergence
6. Scenarios + Events (Sprint 7) - Content
7. Polish (Sprint 8) - Launch ready
8. Sandbox (Sprint 9) - Replayability

The modular approach means if any sprint runs long, you can ship with fewer features or push some to post-launch updates. The focus on making the core economy simulation robust and the combo system rewarding ensures the game has staying power.

**What Makes This Special:**
- Price discovery creates distinct game phases
- Combos teach depth through positive reinforcement
- Cartels add factional warfare without scripting
- Personal goals make NPCs feel human
- Behavior contagion creates visible waves of change
- Supply manipulation gives direct market control
- Random events force adaptation

The game rewards mastery of interconnected systems. Beginners cause chaos, experts orchestrate economic warfare. The "Candy Capitalism" name perfectly captures the spirit: you're not just destroying, you're manipulating markets like a true capitalist demon.

**Timeline Flexibility:**
- **Minimum Viable Game**: End of Sprint 7 (14 weeks)
- **Full v1.0**: End of Sprint 8 (16 weeks)
- **Deluxe Edition**: End of Sprint 9 (18 weeks)

Focus on making the emergence spectacular - that's your competitive advantage. Good luck, and may your candy markets crash spectacularly!

---

## Current Status

- **Sprint 0**: ✅ COMPLETED
- **Sprint 1**: ✅ COMPLETED  
- **Sprint 2**: ✅ COMPLETED
- **Next**: Sprint 3 - Possession System & Basic UI
- **Timeline**: 18 weeks total (4.5 months)
- **Current Phase**: Core trading system complete, ready for player interaction
