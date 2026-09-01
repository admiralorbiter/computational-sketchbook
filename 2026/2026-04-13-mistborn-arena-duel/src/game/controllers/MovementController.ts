import { PlayerEntity } from '../entities/PlayerEntity';
import { InputFrame } from '../input/InputFrame';
import { InputAction } from '../input/InputAction';
import { PlayerState } from '../state/PlayerStateEnum';

export class MovementController {
  public update(entity: PlayerEntity, input: InputFrame, prevInput: InputFrame, delta: number) {
    const state = entity.stateMachine.current;
    
    // Decrease cooldowns
    if (entity.dashCooldownTimerMs > 0) {
      entity.dashCooldownTimerMs -= delta;
    }

    // Skip movement logic if in combat lockout states
    if (state === PlayerState.Hitstun || state === PlayerState.KO || state === PlayerState.Block) {
      this.checkGlobalTransitions(entity); // keep checking fall 
      entity.stateMachine.update(delta);
      return; 
    }

    // Process logic based on current state
    switch (state) {
      case PlayerState.Idle:
      case PlayerState.Run:
        this.handleGroundedMovement(entity, input, prevInput);
        break;
      
      case PlayerState.Jump:
      case PlayerState.Fall:
        this.handleAerialMovement(entity, input);
        break;

      case PlayerState.Dash:
        this.handleDashState(entity);
        break;
        
      default:
        // No custom movement logic in combat states for now
        break;
    }

    // Always update the state machine timer
    entity.stateMachine.update(delta);
    
    // Check global state transitions like falling
    this.checkGlobalTransitions(entity);
  }

  private handleGroundedMovement(entity: PlayerEntity, input: InputFrame, prevInput: InputFrame) {
    const mov = entity.definition.movement;
    
    // Check Dash
    if (input.actions.has(InputAction.Dash) && !prevInput.actions.has(InputAction.Dash) && entity.dashCooldownTimerMs <= 0) {
      entity.stateMachine.transition(PlayerState.Dash);
      // Determine dash direction based on facing if no input, else input direction
      const dashDir = input.actions.has(InputAction.MoveLeft) ? -1 : 
                      input.actions.has(InputAction.MoveRight) ? 1 : 
                      (entity.facingRight ? 1 : -1);
      
      entity.body.setVelocityX(dashDir * mov.dashSpeed);
      entity.body.setVelocityY(0);
      return;
    }

    // Check Jump
    if (input.actions.has(InputAction.Jump) && !prevInput.actions.has(InputAction.Jump)) {
      entity.stateMachine.transition(PlayerState.Jump);
      entity.body.setVelocityY(mov.jumpVelocity);
      return;
    }

    // Horizontal Movement
    this.applyHorizontalInput(entity, input, 1.0);

    // State flip (Idle <-> Run)
    if (Math.abs(entity.body.velocity.x) > 10) {
      if (entity.stateMachine.current !== PlayerState.Run) {
         entity.stateMachine.transition(PlayerState.Run);
      }
    } else {
      if (entity.stateMachine.current !== PlayerState.Idle) {
         entity.stateMachine.transition(PlayerState.Idle);
      }
    }
  }

  private handleAerialMovement(entity: PlayerEntity, input: InputFrame) {
    const mov = entity.definition.movement;
    
    // Can't dash in the air currently as per MVP choice unless we decide otherwise
    // Apply reduced horizontal movement
    this.applyHorizontalInput(entity, input, mov.airControl);

    // Transition to Fall if moving down
    if (entity.stateMachine.current === PlayerState.Jump && entity.body.velocity.y >= 0) {
      entity.stateMachine.transition(PlayerState.Fall);
    }
  }

  private handleDashState(entity: PlayerEntity) {
    const mov = entity.definition.movement;
    
    // Lock vertical movement during dash
    entity.body.setVelocityY(0);

    // Exit dash when duration expires
    if (entity.stateMachine.timerMs >= mov.dashDurationMs) {
      entity.body.setVelocityX(0); // Stop dash momentum hard for precise spacing
      entity.dashCooldownTimerMs = mov.dashCooldownMs;
      
      entity.stateMachine.transition(entity.body.blocked.down ? PlayerState.Idle : PlayerState.Fall);
    }
  }

  private applyHorizontalInput(entity: PlayerEntity, input: InputFrame, controlMultiplier: number) {
    const mov = entity.definition.movement;
    const accel = mov.acceleration * controlMultiplier;
    const decel = mov.deceleration * controlMultiplier;

    if (input.actions.has(InputAction.MoveLeft) && !input.actions.has(InputAction.MoveRight)) {
      entity.body.setAccelerationX(-accel);
      entity.facingRight = false;
    } else if (input.actions.has(InputAction.MoveRight) && !input.actions.has(InputAction.MoveLeft)) {
      entity.body.setAccelerationX(accel);
      entity.facingRight = true;
    } else {
      // No input, decelerate to 0
      entity.body.setAccelerationX(0);
      
      if (entity.body.velocity.x > 0) {
         entity.body.setAccelerationX(-decel);
         if (entity.body.velocity.x - decel * (1/60) < 0) {
             entity.body.setVelocityX(0);
             entity.body.setAccelerationX(0);
         }
      } else if (entity.body.velocity.x < 0) {
         entity.body.setAccelerationX(decel);
         if (entity.body.velocity.x + decel * (1/60) > 0) {
             entity.body.setVelocityX(0);
             entity.body.setAccelerationX(0);
         }
      }
    }

    // Clamp speed
    const maxSpeed = mov.runSpeed;
    if (entity.stateMachine.current !== PlayerState.Dash) {
      if (entity.body.velocity.x > maxSpeed) entity.body.setVelocityX(maxSpeed);
      if (entity.body.velocity.x < -maxSpeed) entity.body.setVelocityX(-maxSpeed);
    }
  }

  private checkGlobalTransitions(entity: PlayerEntity) {
    const s = entity.stateMachine.current;
    
    // Land on the ground
    if (entity.body.blocked.down && (s === PlayerState.Fall || s === PlayerState.Jump)) {
      entity.stateMachine.transition(PlayerState.Idle);
    }
    
    // Fall off a ledge - ignore if in hitstun, hitstun system manages exit
    if (!entity.body.blocked.down && s !== PlayerState.Jump && s !== PlayerState.Fall && s !== PlayerState.Hitstun && s !== PlayerState.KO) {
      entity.stateMachine.transition(PlayerState.Fall);
    }
  }
}
