# Folder Structure

## Proposed Structure

```text
/docs
/src
  /assets
    /audio
    /images
    /sprites
  /config
    gameConfig.ts
    debugConfig.ts
  /data
    /characters
      characterA.ts
      characterB.ts
    /moves
      sharedMoves.ts
      characterAMoves.ts
      characterBMoves.ts
    /stages
      stage01.ts
  /game
    /combat
      BlockSystem.ts
      DamageSystem.ts
      HitboxSystem.ts
      HurtboxSystem.ts
      KnockbackSystem.ts
      MoveExecutor.ts
      ProjectileSystem.ts
    /controllers
      MovementController.ts
      PlayerController.ts
    /entities
      AnchorPointEntity.ts
      PlayerEntity.ts
      ProjectileEntity.ts
    /input
      InputBuffer.ts
      InputFrame.ts
      InputManager.ts
      KeyboardAdapter.ts
      GamepadAdapter.ts
    /match
      MatchController.ts
      RoundController.ts
      SpawnManager.ts
    /scenes
      BootScene.ts
      PreloadScene.ts
      CombatScene.ts
    /state
      StateMachine.ts
      PlayerState.ts
      MatchState.ts
    /ui
      DebugOverlay.ts
      HudView.ts
      HealthBarView.ts
      ResourceBarView.ts
    /utils
      math.ts
      events.ts
      logger.ts
  main.ts
```

## Rules
- scene files should orchestrate, not own all logic
- data files should define values, not perform gameplay logic
- reusable systems must not depend on one specific character unless documented clearly
