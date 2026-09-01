import { PlayerEntity } from '../entities/PlayerEntity';
import { InputFrame } from '../input/InputFrame';
import { InputAction } from '../input/InputAction';
import { PlayerState } from '../state/PlayerStateEnum';
import { getMove } from '../../data/moves/MoveRegistry';
import { EventBus } from '../utils/events';

export class MoveExecutor {
  constructor(private eventBus: EventBus) {}

  public update(entity: PlayerEntity, input: InputFrame, delta: number) {
    if (entity.stateMachine.current === PlayerState.Hitstun || 
        entity.stateMachine.current === PlayerState.KO ||
        entity.stateMachine.current === PlayerState.Dash) {
      return; 
    }

    if (entity.activeMove) {
      this.advanceMoveTiming(entity, delta);
    } else {
      this.checkMoveInitialization(entity, input);
    }
  }

  private checkMoveInitialization(entity: PlayerEntity, input: InputFrame) {
    const isGrounded = entity.stateMachine.current === PlayerState.Idle || entity.stateMachine.current === PlayerState.Run;
    const isAerial = entity.stateMachine.current === PlayerState.Jump || entity.stateMachine.current === PlayerState.Fall;

    if (!isGrounded && !isAerial) return;

    let desiredMoveInput: 'light' | 'heavy' | null = null;
    if (input.actions.has(InputAction.Light)) desiredMoveInput = 'light';
    else if (input.actions.has(InputAction.Heavy)) desiredMoveInput = 'heavy';

    if (!desiredMoveInput) return;

    // Find move in character spec
    const moveId = entity.definition.moves.find(id => getMove(id).input === desiredMoveInput);
    if (!moveId) return;

    const moveDef = getMove(moveId);

    if (isAerial && !moveDef.canUseInAir) return;
    if (entity.resource < moveDef.resourceCost) return;

    // Initialize move
    entity.resource -= moveDef.resourceCost;
    entity.activeMove = moveDef;
    entity.movePhase = 'startup';
    entity.movePhaseTimerMs = 0;
    
    // Lock horizontal velocity completely unless movement impulse exists
    entity.body.setVelocityX(0);
    entity.body.setAccelerationX(0); // Stop accelerating

    if (moveDef.movementImpulse) {
      const dir = entity.facingRight ? 1 : -1;
      entity.body.setVelocity(moveDef.movementImpulse.x * dir, moveDef.movementImpulse.y);
    }

    entity.stateMachine.transition(PlayerState.Attack);
    this.eventBus.emit('move_started', { player: entity });
  }

  private advanceMoveTiming(entity: PlayerEntity, delta: number) {
    if (!entity.activeMove || !entity.movePhase) return;

    entity.movePhaseTimerMs += delta;
    const move = entity.activeMove;

    if (entity.movePhase === 'startup') {
      if (entity.movePhaseTimerMs >= move.startupMs) {
        entity.movePhase = 'active';
        entity.movePhaseTimerMs = 0;
      }
    } 
    else if (entity.movePhase === 'active') {
      if (entity.movePhaseTimerMs >= move.activeMs) {
        entity.movePhase = 'recovery';
        entity.movePhaseTimerMs = 0;
      }
    } 
    else if (entity.movePhase === 'recovery') {
      if (entity.movePhaseTimerMs >= move.recoveryMs) {
        // Move finished
        entity.activeMove = null;
        entity.movePhase = null;
        entity.movePhaseTimerMs = 0;
        
        entity.stateMachine.transition(entity.body.blocked.down ? PlayerState.Idle : PlayerState.Fall);
      }
    }
  }
}
