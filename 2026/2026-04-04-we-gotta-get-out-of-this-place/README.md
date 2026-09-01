# We Gotta Get Out of This Place

A 2D, low-graphics rocket design and flight simulation game built in Rust with macroquad.

This repository is organized as a lightweight design and development pack for the project. The goal is to preserve the systems-driven joy of a Kerbal-like game while staying readable, low-fi, and realistic for a solo developer to build.

## Project Snapshot

- **Genre:** 2D rocket engineering / spaceflight sim
- **Primary fantasy:** Build unstable machines, solve ascent problems, and escape gravity
- **Rendering / engine choice:** Rust + macroquad
- **Approach:** Code-first, custom UI, custom simulation, data-driven content
- **Version 1 scope:** One planet, modular rockets, staging, ascent, orbit, missions, debriefs

## Design Pillars

1. **Readable depth** — easy to understand, hard to master
2. **Systems over spectacle** — physics and tradeoffs matter more than graphics
3. **Fast iteration** — both player and developer should be able to fail, learn, and retry quickly
4. **Failure with feedback** — the game must explain why things went wrong
5. **Small scope, strong identity** — deliberately 2D and focused rather than pretending to be a giant sandbox

## MVP Summary

The MVP should let the player:

- assemble a simple multistage rocket
- launch from a single planet
- manage throttle, rotation, and staging
- read a clear HUD with core telemetry
- enter a simple map view
- complete altitude, space, and orbit missions
- review a debrief and retry quickly

## Documentation Index

- [`docs/01-game-design-document.md`](docs/01-game-design-document.md) — full game design document
- [`docs/02-technical-design.md`](docs/02-technical-design.md) — architecture, modules, runtime model, and implementation strategy
- [`docs/03-roadmap-and-epics.md`](docs/03-roadmap-and-epics.md) — phases, epics, user stories, acceptance criteria, and milestone order
- [`docs/04-ui-ux-and-hud.md`](docs/04-ui-ux-and-hud.md) — menus, HUD, builder UI, map UI, and usability principles
- [`docs/05-testing-and-tooling.md`](docs/05-testing-and-tooling.md) — test strategy, debug features, dev tools, regression planning
- [`docs/06-content-and-data-model.md`](docs/06-content-and-data-model.md) — part schema, mission schema, saves, and balancing conventions
- [`docs/07-dev-setup-and-workflow.md`](docs/07-dev-setup-and-workflow.md) — development stack, folder layout, workflow, and coding practices
- [`docs/08-open-questions-and-decisions.md`](docs/08-open-questions-and-decisions.md) — current decisions made and unresolved design questions

## Recommended Build Order

1. Foundation and fixed-step runtime
2. Single hardcoded rocket launch toy
3. Data-driven rocket and part model
4. Builder UI and staging
5. Orbit/map systems
6. Mission loop and debriefs
7. Debug tooling expansion
8. Polish and feel

## Working Identity

This is not “KSP but smaller.” It is a mission-first, low-fi, highly readable engineering game with a little tension, a little poetry, and a lot of stubbornness.
