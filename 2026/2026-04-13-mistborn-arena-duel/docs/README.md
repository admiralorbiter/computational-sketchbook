# Cosmere Fan Game

A small local-first 2D arena-duelist prototype built with Phaser 3.

The game is inspired by the movement and combat fantasy of Mistborn and Stormlight, while keeping the design small enough to prototype quickly and expand later into light online multiplayer.

## Current Project Goals
- Prove the combat loop is fun
- Validate movement-based power fantasy
- Build a codebase that can grow into networked multiplayer later
- Keep scope small and testable

## MVP Scope
- Local 1v1 match
- 2 prototype characters
- 1 compact stage
- Movement, dash, jump, block
- Light attack, heavy attack, 2 specials per character
- Health, resource meter, round flow
- Training/debug overlays

## Tech Stack
- Phaser 3
- TypeScript
- Vite
- Arcade Physics
- Custom gameplay systems for combat, state, hitboxes, and resource logic

## Design Principles
- Local first, online later
- Small but deep
- Readable powers
- Tight movement and short combos
- Deterministic-ish simulation mindset

## Repository Goals
This repository should remain easy to understand for solo or small-team development. Systems should be modular, data-driven where possible, and instrumented for debugging.

## Directory Structure
See [FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md) for the full annotated layout.

## Getting Started
1. Install dependencies
2. Start the dev server
3. Open the game in browser
4. Use placeholder assets until gameplay is validated

## Initial Development Priorities
1. Movement controller
2. Combat state machine
3. Hitbox/hurtbox pipeline
4. Character data definitions
5. Match loop
6. Debug tooling

## Non-Goals for MVP
- Matchmaking
- Ranked systems
- Account systems
- Full lore adaptation
- Large roster
- Story mode
- Cosmetics

## Long-Term Expansion
After the local prototype is fun and stable, the game can be extended with:
- online room-based multiplayer
- input sync / rollback experimentation
- additional characters
- more stages
- AI opponents
