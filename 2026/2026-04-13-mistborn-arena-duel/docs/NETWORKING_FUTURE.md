# Networking Future

## Goal
Prepare the local prototype for future light online multiplayer without implementing it prematurely.

## Assumed Model
For future multiplayer, the most realistic direction is a small room-based 1v1 model using input sync or rollback-style experimentation.

## Decisions to Preserve Now
- compact input representation
- stable update order
- minimal randomness
- serializable match state
- gameplay not driven by VFX/audio timing

## Good Prep Tasks
- record inputs by frame
- log match events
- serialize player/match state snapshots for debugging
- keep move logic deterministic-ish

## Avoid
- hidden timeouts not tracked in state
- relying on physics oddities for gameplay outcomes
- logic buried in animation callbacks

## Networking Not in MVP
- matchmaking
- dedicated servers
- spectator mode
- ranking
