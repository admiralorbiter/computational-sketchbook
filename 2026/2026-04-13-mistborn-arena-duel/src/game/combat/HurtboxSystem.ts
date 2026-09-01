import * as Phaser from 'phaser';
import { PlayerEntity } from '../entities/PlayerEntity';
import { HitboxSystem } from './HitboxSystem';
import { EventBus } from '../utils/events';
import { PlayerState } from '../state/PlayerStateEnum';

export class HurtboxSystem {
  constructor(private eventBus: EventBus) {}

  public update(players: PlayerEntity[], hitboxSystem: HitboxSystem) {
    for (const box of hitboxSystem.activeHitboxes) {
      const boxRect = new Phaser.Geom.Rectangle(
        box.worldX - box.def.width / 2,
        box.worldY - box.def.height / 2,
        box.def.width,
        box.def.height
      );

      for (const defender of players) {
        if (defender === box.attacker) continue;
        if (box.alreadyHit.has(defender)) continue;
        if (defender.stateMachine.current === PlayerState.KO) continue;

        const hurtboxRect = new Phaser.Geom.Rectangle(
          defender.x - defender.width / 2,
          defender.y - defender.height / 2,
          defender.width,
          defender.height
        );

        if (Phaser.Geom.Rectangle.Overlaps(boxRect, hurtboxRect)) {
          // Check Block
          const isBlocking = defender.stateMachine.current === PlayerState.Block;
          
          // Frontal check
          // If attacker is to the left, defender should look left to block
          const isAttackerLeft = box.attacker.x < defender.x;
          const isFrontal = (isAttackerLeft && !defender.facingRight) || (!isAttackerLeft && defender.facingRight);

          if (isBlocking && isFrontal) {
            box.alreadyHit.add(defender);
            this.eventBus.emit('block_success', { attacker: box.attacker, defender, hitboxDef: box.def });
          } else {
            box.alreadyHit.add(defender);
            this.eventBus.emit('move_hit', { attacker: box.attacker, defender, hitboxDef: box.def });
          }
        }
      }
    }
  }
}
