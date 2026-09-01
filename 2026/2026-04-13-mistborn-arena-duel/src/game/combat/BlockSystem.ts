import { PlayerEntity } from '../entities/PlayerEntity';
import { InputFrame } from '../input/InputFrame';
import { InputAction } from '../input/InputAction';
import { PlayerState } from '../state/PlayerStateEnum';

export class BlockSystem {
  public update(entity: PlayerEntity, input: InputFrame) {
    const currentState = entity.stateMachine.current;
    
    // Cannot block if locked in these states
    if (currentState === PlayerState.Hitstun || 
        currentState === PlayerState.KO || 
        currentState === PlayerState.Attack ||
        currentState === PlayerState.Dash) {
      return;
    }

    // Only ground block for MVP
    const isGrounded = entity.body.blocked.down;
    
    if (input.actions.has(InputAction.Block) && isGrounded) {
      if (currentState !== PlayerState.Block) {
        entity.body.setVelocityX(0); // Stop moving immediately
        entity.body.setAccelerationX(0); // Stop accelerating
        entity.stateMachine.transition(PlayerState.Block);
      }
    } else {
      if (currentState === PlayerState.Block) {
        // Exit block naturally if no hitstun applies (hitstun system controls force exit)
        if (entity.hitstunTimerMs <= 0) {
          entity.stateMachine.transition(PlayerState.Idle);
        }
      }
    }
  }
}
