# Product Requirements Document

## Product Name
Cosmere Fan Game

## Product Summary
A small-scale 2D local-first combat prototype inspired by Mistborn and Stormlight movement/combat fantasy, built in Phaser 3 and structured for possible expansion into light online multiplayer.

## Problem Statement
We want to create a fan game prototype that captures high-mobility magical dueling in a way that is readable, fun, and practical to develop in Phaser.

## Objective
Ship a local 1v1 prototype that proves:
- movement is satisfying
- combat is understandable and skill-based
- character abilities create distinct playstyles
- the codebase can support further iteration and future networking

## Target Audience
- fans of movement-heavy combat games
- players who enjoy small competitive duels
- Cosmere fans interested in character fantasy
- dev team validating technical feasibility

## Success Criteria
- first-time players understand controls within 2 minutes
- both prototype characters feel distinct within 1 match
- matches are fun with placeholder art
- local play exposes a clear path to tuning and expansion

## MVP Requirements
- local 1v1
- 2 playable characters
- 1 stage
- movement + attacks + specials + guard
- health/resource UI
- match flow and restart
- debug overlays

## Non-Functional Requirements
- stable 60 FPS target on modern desktop browser
- deterministic-ish combat resolution
- tunable gameplay values
- maintainable modular code
- minimal hidden coupling between systems

## Constraints
- small team / likely solo-heavy development
- browser runtime
- fan project scope
- must avoid overbuilding backend/networking early

## Risks
- overscoping character powers
- unclear genre direction
- excessive dependence on physics engine behavior
- hardcoded combat rules that block iteration later
