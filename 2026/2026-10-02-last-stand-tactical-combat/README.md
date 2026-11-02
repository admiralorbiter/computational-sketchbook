# Last Stand: Tactical Combat

**Working Title** — a tactical defense game distilling RimWorld's raid combat into a focused, replayable experience.

## Concept

Design the battlefield. Give your people intent. Fight the battle when the plan meets reality.

A top-down tactical game where you prepare defenses, issue doctrinal orders to a squad, then fight real-time battles with meaningful player micro at the command level — not the maintenance level.

## Core Fantasy

I build a plan. I prepare a battlefield. Then a chaotic system tests my plan, and I intervene when it starts breaking.

## Inspirations

| Game | What to steal |
|------|---------------|
| RimWorld | Emergent systems, data-driven design (Defs), storytelling through simulation, mod ecosystem ideas |
| StarCraft | RTS control language (box select, control groups, attack-move), micro skill ceiling |
| Frozen Synapse | Plan/execute cadence, WEGO elements |
| No Plan B | Planning vs autonomous execution separation |
| Gratuitous Space Battles | The "design then watch" end of the spectrum (we sit one step back toward RTS) |
| Combat Extended (mod) | Ballistic trajectories, suppression as mechanic, weapon role differentiation |
| Defensive Positions (mod) | Remembered positions, quick recall |
| Achtung! (mod) | Group commands, formations |
| Search and Destroy (mod) | Autonomous target finding, intervention-only control |
| CAI 5000 (mod) | Raider tactical AI, cover-seeking, flanking, fog of war |
| Cataclismo | Structural integrity, collapsing structures crushing units |

## Project Structure

```
docs/              — Game design documents
  gdd.md           — Full game design document
  poc-spec.md      — Proof of concept specification (Battle 001)
  combat-math.md   — All combat math: weapons, cover, suppression, TTK
  roadmap.md       — Development phases and milestones
  technical-architecture.md — Engine choice, project structure
prototype/         — Godot 4.x project
```

## Status

🟢 **Implementation & Testing Phase** — Godot 4.7.2 is installed and verified. All 36+ prototype source files compile cleanly.

## Running & Testing

- **Launch Game:** Run [launch_game.bat](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-02-last-stand-tactical-combat/launch_game.bat) or execute:
  ```powershell
  godot --path prototype
  ```
- **Open Godot Editor:** Run [open_editor.bat](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-02-last-stand-tactical-combat/open_editor.bat) or execute:
  ```powershell
  godot --editor --path prototype
  ```

