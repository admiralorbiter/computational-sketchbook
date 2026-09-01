# Candy Capitalism - Technical Architecture

## Overview

Candy Capitalism uses a modular, event-driven architecture designed for emergent gameplay and easy maintenance. The system is built around the principle of "simple rules, complex behavior" where individual systems interact to create sophisticated gameplay.

## System Dependencies

```
Game (main.py)
├── GameWorld (central coordinator)
│   ├── Economy (candy values, market prices)
│   ├── PossessionSystem (player control)
│   ├── RumorSystem (information warfare)
│   ├── EventSystem (decoupled communication)
│   └── SpatialGrid (performance optimization)
├── Entities (Kid, House, Rumor, TradingBloc)
├── AI (behavior trees, decision making)
├── UI (HUD, menus, popups)
└── Rendering (camera, sprites, effects)
```

## Core Systems

### 1. Game Loop Architecture

**Update Frequency Tiers:**
- **Tier 1 (60 FPS)**: Movement, rendering, input handling
- **Tier 2 (0.5 Hz)**: AI decision making, trading logic
- **Tier 3 (0.1 Hz)**: Market calculations, bloc formation

**Benefits:**
- Maintains 60 FPS with 30+ entities
- Heavy AI logic doesn't block rendering
- Scalable performance model

### 2. Event-Driven Communication

**Event Bus Pattern:**
```python
# Systems publish events
event_system.publish_trade_completed(kid_a, kid_b, offer, request)

# Other systems subscribe
event_system.subscribe(EventType.TRADE_COMPLETED, on_trade_completed)
```

**Benefits:**
- Loose coupling between systems
- Easy to add new features
- Supports complex interactions
- Makes testing easier

### 3. Spatial Partitioning

**Grid-Based Optimization:**
- Divides world into 100x100 unit cells
- O(1) neighbor queries instead of O(n)
- Essential for 30+ entity performance
- Supports both kids and houses

### 4. Configuration Management

**JSON-Based Tuning:**
- All game values in config files
- Hot-reloadable during development
- Easy balancing without code changes
- Supports different difficulty levels

## Entity System

### Base Entity
```python
class BaseEntity:
    def __init__(self, entity_id, position)
    def update(self, dt)
    def render(self, screen, camera)
    def move_toward(self, target, speed, dt)
```

### Kid Entity
- **States**: IDLE, MOVING_TO_HOUSE, TRICK_OR_TREATING, SEEKING_TRADE, IN_TRADE, FLEEING
- **Personality**: VALUE_INVESTOR, MOMENTUM_TRADER, HOARDER, SOCIAL_TRADER, PANIC_SELLER
- **Mood**: HAPPY, NEUTRAL, ANXIOUS, GREEDY, PANIC
- **AI**: FSM-based behavior with personality-driven decisions

### House Entity
- **Properties**: Candy quality, dispense rate, attraction radius
- **Powers**: Can be cursed or blessed by player
- **Effects**: Influence kid behavior and candy distribution

## AI Architecture

### Finite State Machine
```python
class Kid:
    def ai_tick(self, world):
        if self.has_overdue_debt():
            self.seek_debt_repayment(world)
        elif self.personal_goal and self.personal_goal.is_urgent():
            self.pursue_goal(world)
        else:
            self.seek_trade_partner(world)
```

### Behavior Contagion
- Kids observe successful strategies
- Copy behaviors that work
- Creates emergent fads and trends
- "Monkey see, monkey do" dynamics

### Trading Bloc Formation
- Union-Find algorithm for clustering
- Forms from frequent trading relationships
- Provides information advantages
- Creates factional warfare

## Economy System

### Price Discovery
1. **Phase 1 (0-2 min)**: Pure chaos, random beliefs
2. **Phase 2 (2-5 min)**: Market stabilizing, patterns emerge
3. **Phase 3 (5+ min)**: Established market, harder to manipulate

### Market Dynamics
- **Real Values**: Objective candy worth
- **Believed Values**: What kids think candy is worth
- **Market Prices**: Emerge from actual trades
- **Trends**: Momentum and volatility calculations

### Trading Logic
```python
def evaluate_trade(kid, offer, request):
    base_delta = calculate_value_delta(offer, request)
    threshold = kid.personality.get_threshold()
    mood_modifier = kid.mood.get_modifier()
    goal_bonus = kid.personal_goal.evaluate_trade(offer, request)
    return base_delta - (threshold * mood_modifier) + goal_bonus
```

## Rendering System

### Layered Rendering
1. **Background**: World tiles, houses
2. **World**: Kids, candy, effects
3. **HUD**: Energy bar, possessed kid info
4. **Popups**: Trade windows, rumor menus
5. **Overlay**: Debug info, stats

### Camera System
- World-to-screen coordinate conversion
- Zoom and pan support
- Follow modes for possessed kid
- Smooth transitions

## UI System

### Event Handling
- Top-down event processing
- Popups consume events first
- HUD elements handle input
- World objects last

### UI Elements
- Base UIElement class
- Button, Label, Panel subclasses
- Consistent styling and behavior
- Easy to extend and modify

## Performance Optimization

### Object Pooling
- Reuse frequently allocated objects
- Rumors, particles, trade records
- Reduces garbage collection pressure
- Improves frame rate stability

### Caching
- Pathfinding results
- Rendered text surfaces
- Expensive calculations
- Spatial grid queries

### Profiling
- Built-in performance monitoring
- Frame time tracking
- AI tick timing
- Memory usage monitoring

## Data Flow

### Update Loop
```
1. Handle Input Events
2. Update Game State (60 FPS)
3. Update AI (0.5 Hz)
4. Update Systems (0.5 Hz)
5. Update Rendering (60 FPS)
6. Present Frame
```

### Event Flow
```
Player Action → Event System → Affected Systems → Entity Updates → Rendering
```

## Testing Strategy

### Unit Tests
- Core logic functions
- Economy calculations
- AI decision making
- Trading evaluations

### Integration Tests
- System interactions
- Event propagation
- End-to-end scenarios
- Performance benchmarks

### Playtesting
- Every sprint completion
- Focus on emergent behavior
- Balance and difficulty
- User experience

## Scalability

### Horizontal Scaling
- Add more kids (up to 30)
- Add more houses
- Add more scenarios
- Add more candy types

### Vertical Scaling
- Improve AI sophistication
- Add more personality types
- Add more rumor types
- Add more combo patterns

## Maintenance

### Code Organization
- Clear separation of concerns
- Consistent naming conventions
- Comprehensive documentation
- Regular refactoring

### Configuration
- All tunable values in JSON
- Version control for configs
- Easy to modify and test
- Supports different builds

### Debugging
- Built-in debug overlay
- Event logging
- Performance profiling
- State inspection tools

## Future Extensibility

### New Systems
- Easy to add new game systems
- Event-driven integration
- Minimal coupling
- Clear interfaces

### New Features
- Modular design supports additions
- Configuration-driven behavior
- Event system handles new interactions
- UI system supports new elements

### Platform Support
- Pygame is cross-platform
- Configuration files are portable
- No platform-specific code
- Easy to package and distribute

## Conclusion

This architecture supports the core design goals of emergent gameplay, easy maintenance, and scalable performance. The modular design allows for incremental development while the event-driven communication ensures systems can interact naturally without tight coupling.

The focus on configuration and testing ensures the game can be balanced and polished effectively, while the performance optimizations allow for the complex AI behaviors that make the game engaging.
