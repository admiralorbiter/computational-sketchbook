# Candy Capitalism - Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Sprint 4: Rumor System
- Sprint 5: Debt & Mood Systems
- Sprint 6: Cartels, Behavior Contagion & Personality Polish
- Sprint 7: Scenarios, Random Events & Progression
- Sprint 8: Polish, Juice & Launch Prep
- Sprint 9: Sandbox Mode & Advanced Features

## [0.3.0] - 2024-12-22 - Sprint 3 Complete

### Added
- **Possession System**
  - Chaos Energy system with regeneration and drain mechanics
  - Click-to-possess/kid interaction for player control
  - Possessed kid movement with WASD/arrow keys
  - Release possession with ESC key
  - Energy bar HUD displaying current chaos energy
  - Possessed kid info panel showing inventory and stats

- **Player-Controlled Trading**
  - Trade window UI with drag-and-drop interface
  - Select candy to offer and request from target kid
  - Trade value calculation (good/bad trade indication)
  - Chaos point rewards for bad trades (2x trade value)
  - Trade preview showing chaos gain potential
  - Player can force bad trades to earn chaos points

- **Supply Manipulation Powers**
  - Curse House power reduces candy supply (-50%)
  - Bless House power increases candy supply (+50%)
  - House cooldown system (30 seconds)
  - Energy cost for powers (curse: 30, bless: 25)
  - Chaos point rewards (curse: 5, bless: 3)

- **AI Behavior Updates**
  - Kids avoid cursed houses
  - Kids prefer blessed houses (70% probability)
  - House selection filters out cursed houses
  - Natural supply-side manipulation creates economic effects

- **Visual Polish**
  - Pulsing red glow for cursed houses
  - Pulsing green/gold glow for blessed houses
  - Enhanced possession glow with pulsing red aura
  - Particle effects for curse/bless activation
  - Multi-layer glow effects with alpha blending
  - Enhanced visibility for possessed kids

- **UI Improvements**
  - Trade window shows chaos gain preview for bad trades
  - Chaos Score Display integrated with trade system
  - Power menu for house manipulation
  - Improved possession state indication
  - Updated controls documentation

### Technical Details
- **Controls**: P key for pause/unpause, ESC for release possession
- **Interaction**: Click different kid while possessing to initiate trade
- **T Key**: Toggle trade window (when possessing)
- **Performance**: Maintains 60 FPS with all visual effects active
- **Architecture**: Clean event-driven UI system with callbacks
- **Testing**: 210 unit tests passing, manual testing scenarios documented and verified
- **Rendering**: Safe drawing wrappers prevent crashes from invalid color/coordinate arguments

## [0.2.0] - 2024-12-20 - Sprint 2 Complete

### Added
- **Core Trading System**
  - 1-for-1 and multi-item trades (1-3 candy types per trade)
  - Autonomous trading AI with personality-based evaluation
  - Trade proposal generation and acceptance logic
  - Kids autonomously initiate and complete trades

- **Economy System**
  - Real values for all candy types loaded from config
  - Market price calculations based on trade history
  - Trade history tracking with configurable window size
  - Volatility and trend strength calculations
  - Price discovery mechanics with belief updates

- **Price Discovery System**
  - Configurable modes: fixed, random, convergent
  - Kids start with different believed values
  - Belief updates from completed trades
  - Convergence toward real values over time
  - Learning rate configuration

- **Visual Feedback**
  - Trade particles moving between kids
  - Floating text showing trade details
  - Market ticker displaying real-time prices
  - Economy debug overlay (press 'E' key)
  - Enhanced inventory display with value information

- **Trading AI Logic**
  - Personality-based trade evaluation (VALUE_INVESTOR, PANIC_SELLER, etc.)
  - Mood modifiers affecting trade decisions
  - Candy preference system
  - Partner search using spatial grid
  - Trade cooldown and range limitations

- **Testing Suite**
  - 12 new unit tests for trading logic
  - Tests for candy type system, inventory management, trade evaluation
  - Tests for trading AI partner finding
  - All 190 tests passing (100% pass rate)

### Technical Details
- **Performance**: Maintains 60 FPS with trading active
- **Configuration**: All trading parameters configurable via JSON
- **Architecture**: Clean separation between economy, AI, and visualization
- **Testing**: Comprehensive test coverage for all new systems

### Controls Added
- **E Key**: Toggle economy debug overlay
- **I Key**: Toggle inventory display (enhanced with values)
- **Help Overlay**: Updated with new controls

## [0.1.0] - 2024-12-19 - Sprint 1 Complete

### Added
- **Core World System**
  - Procedural neighborhood map generation with JSON configuration
  - 15-20 houses with quality levels (A, B, C) and visual indicators
  - House candy dispensing system with cooldown mechanics
  - Spatial grid optimization for efficient neighbor queries

- **Kid Entity System**
  - State machine with IDLE, MOVING_TO_HOUSE, TRICK_OR_TREATING states
  - 5 personality types: VALUE_INVESTOR, MOMENTUM_TRADER, HOARDER, SOCIAL_TRADER, PANIC_SELLER
  - Autonomous movement and pathfinding to houses
  - Candy inventory system with type tracking
  - Collision detection and separation forces

- **A* Pathfinding System**
  - Full A* implementation with obstacle avoidance
  - Pathfinding grid with configurable cell size
  - Path caching for performance optimization
  - Dynamic obstacle management

- **Camera System**
  - World-to-screen coordinate conversion
  - Smooth zoom and pan with mouse wheel support
  - Camera bounds and smooth movement
  - Debug camera controls

- **Rendering Pipeline**
  - Layered rendering system (background, entities, UI, debug)
  - Sprite caching and font management
  - Debug overlay with comprehensive information
  - Help overlay with control instructions

- **Polish Features**
  - Particle effects for candy dispensing
  - House cooldown visualization with progress bars
  - Inventory UI with candy breakdown (toggle with 'I' key)
  - Personality indicators on kids
  - Kid collision detection and separation
  - Enhanced debug overlay

- **Testing Suite**
  - 178 tests with 100% pass rate
  - Unit tests for all core systems
  - Integration tests for complete workflows
  - Performance tests with reasonable thresholds
  - Manual testing scenarios documented

### Technical Details
- **Performance**: 60 FPS target maintained with 10+ kids
- **Architecture**: Event-driven, modular design with clean separation of concerns
- **Configuration**: JSON-based configuration for all game parameters
- **Testing**: Comprehensive pytest suite with unit and integration tests

## [0.1.0] - 2025-10-25

### Added
- **Sprint 0: Project Setup** - Complete foundation for Candy Capitalism development

#### Core Architecture
- Game loop with 60 FPS target
- State machine for game states (MAIN_MENU, PLAYING, PAUSED, etc.)
- Configuration management system with JSON configs
- Event-driven communication system
- Spatial partitioning for performance optimization

#### Entity System
- Base entity class with position, velocity, and update/render hooks
- Kid entity with AI states, personality types, and trading capabilities
- House entity with candy dispensing and power effects (curse/bless)
- Rumor entity for information warfare
- Trading bloc entity for cartel formation

#### Game Systems
- Economy system with price discovery and market dynamics
- Possession system for player control of kids
- Rumor system for spreading misinformation
- Event system for decoupled communication
- Game world coordinator managing all entities and systems

#### Utilities
- Vector2 class for 2D math operations
- Spatial grid for efficient neighbor queries
- Helper functions for common operations
- Coordinate conversion utilities

#### Rendering Foundation
- Renderer class for world rendering
- Camera system for world-to-screen conversion
- UI manager with layered rendering
- Base UI element classes

#### Configuration
- Candy types configuration (6 types with values and properties)
- Game settings (screen size, FPS, AI rates, etc.)
- Personality types configuration
- Extensible JSON-based config system

#### Testing
- Pytest configuration and fixtures
- Unit tests for economy system
- Integration tests for trading system
- Test structure for future development

#### Documentation
- Development philosophy document
- Technical architecture overview
- Sprint progress tracking
- Comprehensive code documentation

#### Project Structure
```
/src
  /core          - Game loop, managers, constants
  /entities      - Kid, House, Rumor, TradingBloc
  /systems       - Economy, Possession, Rumor, Event
  /ai            - AI behaviors and decision making
  /ui            - User interface elements
  /rendering     - Renderer, camera, sprite manager
  /utils         - Vector2, spatial grid, helpers
/config          - JSON configuration files
/assets          - Art and audio assets
/tests           - Unit and integration tests
/docs            - Development documentation
```

### Technical Details
- **Python Version**: 3.12.0
- **Engine**: Pygame >= 2.5.0
- **Testing**: Pytest >= 7.4.0
- **Architecture**: Event-driven, modular design
- **Performance**: 60 FPS target with 30+ AI agents
- **Update Frequencies**: 60 FPS rendering, 0.5 Hz AI, 0.1 Hz slow updates

### Success Criteria Met
- [x] Game window opens and runs at 60 FPS with empty scene
- [x] Project structure supports modular development
- [x] All skeleton files have docstrings and basic structure
- [x] Config loading works
- [x] Documentation clearly explains development approach
- [x] Test structure in place with example tests
- [x] Foundation ready for Sprint 1 development

### Known Issues
- Rendering system is placeholder (will be implemented in Sprint 1)
- AI behavior is placeholder (will be implemented in Sprint 2)
- Trading system is placeholder (will be implemented in Sprint 2)
- No actual gameplay yet (foundation only)

### Next Release
- **v0.2.0** - Sprint 1: Core World & Movement
  - Neighborhood map generation
  - Kid autonomous movement
  - Basic pathfinding
  - House candy dispensing
  - 10+ kids moving around neighborhood

---

## Development Notes

### Sprint 0 Completion
This release represents the complete foundation for Candy Capitalism. All core architecture is in place, including:

1. **Modular Design**: Clean separation of concerns with short, focused files
2. **Event-Driven**: Loose coupling between systems via event bus
3. **Performance-First**: Spatial partitioning and tiered update frequencies
4. **Configuration-Driven**: All tunable values in JSON configs
5. **Test-Ready**: Comprehensive test structure with examples
6. **Documentation**: Clear philosophy and architecture guides

The project is now ready for Sprint 1 development, which will focus on implementing the core world and movement systems to create the first playable version.

### Key Architectural Decisions
- **Pygame**: Chosen for simplicity and 2D performance
- **Python**: Rapid prototyping and AI/data processing
- **Event Bus**: Enables loose coupling and easy feature addition
- **Spatial Grid**: Essential for 30+ entity performance
- **JSON Configs**: Easy tuning without code changes
- **Modular Files**: Each file has single responsibility

### Performance Targets
- **Rendering**: 60 FPS with simple 2D graphics
- **AI Updates**: 0.5 Hz (every 2 seconds) for 30+ kids
- **Spatial Queries**: O(1) neighbor finding via grid
- **Memory**: Object pooling for frequent allocations
- **Scalability**: Support for 30+ kids, 25+ houses

This foundation provides a solid base for building the complex economic simulation that will make Candy Capitalism unique and engaging.
