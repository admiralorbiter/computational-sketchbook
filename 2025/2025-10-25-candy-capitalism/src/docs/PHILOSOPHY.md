# Candy Capitalism - Development Philosophy

## Core Principles

### 1. Short, Modular Files
- Each file should have a single, clear responsibility
- Keep files under 200 lines when possible
- Use clear, descriptive names for classes and functions
- Prefer composition over inheritance

### 2. Backend-Heavy Focus
- Invest time in robust AI and economy systems
- UI can be simple, emergence must be spectacular
- Trading logic should be bulletproof
- Rumor propagation should feel organic

### 3. Emergence Over Scripting
- Simple rules create complex behavior
- No scripted events, just systems interacting
- Players discover strategies you didn't plan
- Let the systems tell the story

### 4. Systems Integration
- All systems should interact naturally
- Changes in one system should ripple through others
- Avoid tight coupling between systems
- Use events for loose coupling

## File Organization

### Hierarchy-Based Structure
```
/src
  /core          - Game loop, managers, constants
  /entities      - Game objects (Kid, House, Rumor)
  /systems       - Game systems (Economy, Possession, AI)
  /ai            - AI behaviors and decision making
  /ui            - User interface elements
  /rendering     - Rendering and camera systems
  /utils         - Helper functions and utilities
```

### Naming Conventions
- Classes: PascalCase (e.g., `TradingBloc`)
- Functions: snake_case (e.g., `calculate_market_price`)
- Constants: UPPER_CASE (e.g., `MAX_ENERGY`)
- Files: snake_case (e.g., `possession_system.py`)

## Development Approach

### Incremental Complexity
- Start simple (movement + trading)
- Add one system at a time
- Playtest for emergence at each stage
- Each sprint builds on previous work

### Performance First
- Optimize for 30+ AI agents
- Use spatial partitioning for neighbor queries
- Tiered update frequencies (60 FPS, 0.5 Hz AI, 0.1 Hz slow)
- Profile early and often

### Configuration-Driven
- All tunable values in JSON configs
- Easy to balance without code changes
- Support for different difficulty levels
- A/B testing friendly

## Code Quality

### Documentation
- Every class and function needs a docstring
- Explain the "why" not just the "what"
- Include examples for complex functions
- Keep comments up to date

### Testing
- Unit tests for core logic (economy, AI)
- Integration tests for system interactions
- Playtest every sprint
- Test for edge cases and exploits

### Error Handling
- Fail gracefully with helpful messages
- Log errors for debugging
- Don't let one bug crash the whole game
- Provide fallbacks for missing data

## Game Design Philosophy

### Player Agency
- Give players meaningful choices
- Every action should have consequences
- Reward clever strategies
- Don't punish experimentation

### Emergent Gameplay
- Let players discover combos
- Don't explain everything upfront
- Create "aha!" moments
- Support multiple play styles

### Feedback Loops
- Clear cause and effect
- Immediate feedback for actions
- Long-term consequences visible
- Make systems understandable

## Technical Decisions

### Why Pygame?
- Simple 2D graphics
- Good performance for this scope
- Easy to learn and debug
- Cross-platform support

### Why Python?
- Rapid prototyping
- Easy to modify and extend
- Good for AI and data processing
- Large ecosystem

### Why Event-Driven?
- Loose coupling between systems
- Easy to add new features
- Supports complex interactions
- Makes testing easier

## Success Metrics

### Technical
- 60 FPS with 30+ kids
- Zero critical bugs
- Clean, maintainable code
- All systems work together

### Gameplay
- Players discover unintended strategies
- Each playthrough feels different
- "Aha!" moments when economy collapses
- Satisfying feedback for mastery

### Development
- Can add features without breaking existing code
- Easy to tune game balance
- Clear separation of concerns
- Documentation is helpful and accurate

## Anti-Patterns to Avoid

### Don't
- Put everything in one giant file
- Hardcode values that should be configurable
- Create circular dependencies
- Optimize prematurely
- Skip testing

### Do
- Break complex functions into smaller ones
- Use configuration files for tuning
- Design for loose coupling
- Profile before optimizing
- Test early and often

## Conclusion

The goal is to create a game where simple rules generate complex, emergent behavior. The code should be clean, modular, and easy to understand. The gameplay should reward mastery and experimentation. Most importantly, the systems should work together to create something greater than the sum of their parts.

Remember: We're not just building a game, we're building a living, breathing economic simulation that players can manipulate and master. The code is the foundation that makes this possible.
