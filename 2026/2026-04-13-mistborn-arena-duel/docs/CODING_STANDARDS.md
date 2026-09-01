# Coding Standards

## General Principles
- prefer small focused classes/modules
- avoid god objects
- prefer explicit data over hidden defaults
- keep gameplay authority separate from effects/animation
- document non-obvious gameplay assumptions

## TypeScript Rules
- prefer explicit interfaces for gameplay data
- avoid `any`
- use enums/constants for state identifiers
- keep scene-to-system contracts typed

## Gameplay Rules
- do not hardcode balance values inside scene code
- do not let animation be the only source of gameplay timing truth
- do not use random combat effects without documentation and strong need

## Debugging Rules
- important systems should expose debug state when debug mode is enabled
- invalid state transitions should log warnings in dev mode

## Naming Rules
- entities are nouns
- controllers/systems describe responsibilities
- move IDs should be stable and readable
