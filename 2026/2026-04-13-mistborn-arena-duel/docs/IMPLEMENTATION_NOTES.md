# Implementation Notes

## Recommended Early Shortcut
Use placeholder rectangles/circles and text labels for almost everything until the combat loop is proven.

## Strong Warning
Do not attach gameplay timing directly to sprite animation completion callbacks in the first implementation.

## Better Approach
Gameplay timing should be owned by move/state timers. Animation should follow gameplay state.

## Another Warning
Do not put per-character special logic directly inside CombatScene.

## Better Approach
Create reusable systems and inject character data or small ability hooks.
