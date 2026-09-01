import { EventBus } from '../utils/events';
import { PlayerState } from '../state/PlayerStateEnum';
import { PlayerEntity } from '../entities/PlayerEntity';

export class DamageSystem {
  constructor(private eventBus: EventBus) {
    this.eventBus.on('move_hit', (payload) => {
      const { defender, hitboxDef } = payload;
      
      defender.health = Math.max(0, defender.health - hitboxDef.damage);
      defender.hitstunTimerMs = hitboxDef.hitstunMs || 300;
      defender.stateMachine.transition(PlayerState.Hitstun);
      
      // Hitstop logic
      payload.attacker.hitstopTimerMs = 80;
      defender.hitstopTimerMs = 80;
      
      this.eventBus.emit('hitstun_started', { player: defender, durationMs: defender.hitstunTimerMs });
      
      if (defender.health <= 0) {
        defender.stateMachine.transition(PlayerState.KO);
        this.eventBus.emit('player_ko', { player: defender });
      }
    });

    this.eventBus.on('block_success', (payload) => {
      const { defender, hitboxDef } = payload;
      
      // Chip damage if needed, for MVP we can do 0 damage
      // Apply blockstun
      defender.hitstunTimerMs = hitboxDef.blockstunMs || 150; 
      
      payload.attacker.hitstopTimerMs = 60;
      defender.hitstopTimerMs = 60;
    });
  }

  public update(players: PlayerEntity[], delta: number) {
    for (const player of players) {
      if (player.hitstopTimerMs > 0) {
         player.hitstopTimerMs -= delta;
         // Freeze velocity
         player.body.setVelocity(0, 0);
         player.body.setAcceleration(0, 0);
      }
      
      if (player.hitstunTimerMs > 0) {
        player.hitstunTimerMs -= delta;
        if (player.hitstunTimerMs <= 0) {
          // Exit hitstun
          player.hitstunTimerMs = 0;
          if (player.stateMachine.current === PlayerState.Hitstun || player.stateMachine.current === PlayerState.Block) {
             player.stateMachine.transition(player.body.blocked.down ? PlayerState.Idle : PlayerState.Fall);
          }
        }
      }
    }
  }
}
