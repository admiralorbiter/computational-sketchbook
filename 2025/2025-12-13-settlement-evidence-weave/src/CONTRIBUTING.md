# Contributing to Settlement

## Getting Started

1. **Fork and clone** the repository
2. **Install dependencies:** `npm install`
3. **Start dev server:** `npm run dev`
4. **Read the roadmap:** `docs/Settlement_Technical_Roadmap.md`

## Development Guidelines

### Code Style

- Use TypeScript strictly (no `any` unless necessary)
- Follow existing naming conventions
- Keep functions focused and pure when possible
- Add JSDoc comments for public APIs

### Architecture Principles

1. **Separation of Concerns:**
   - Pure logic in `systems/puzzle/logic/` (no Phaser)
   - Rendering in `systems/puzzle/view/` (Phaser only)
   - State management in `systems/core/`

2. **Testability:**
   - Pure functions/classes are easier to test
   - Keep Phaser dependencies out of core logic
   - Write unit tests for puzzle logic

3. **Modularity:**
   - Each system should be self-contained
   - Use dependency injection where helpful
   - Avoid global state (use GameStateManager)

### Making Changes

1. **Check the roadmap** - Is this feature planned?
2. **Create a branch** - `feature/description` or `fix/description`
3. **Write tests** - Especially for new logic
4. **Test manually** - Play through the game
5. **Update docs** - If adding new systems or changing behavior

### Testing Requirements

- New logic should have unit tests
- Test edge cases (empty grids, boundary conditions)
- Use deterministic RNG for tests
- Manual testing for UI/UX changes

### Pull Request Process

1. **Update roadmap** if adding new features
2. **Add tests** for new functionality
3. **Update README** if changing setup/usage
4. **Write clear PR description** explaining what and why
5. **Link to roadmap** if implementing a planned feature

## Feature Priorities

See `docs/Settlement_Technical_Roadmap.md` for the full plan. Current focus:

1. **Phase 1 Polish** - Playtesting and tuning
2. **Phase 2** - Board & Resource UI
3. **Phase 3** - Narrative Engine

## Questions?

- Check the roadmap document
- Review existing code for patterns
- Ask in issues or discussions

