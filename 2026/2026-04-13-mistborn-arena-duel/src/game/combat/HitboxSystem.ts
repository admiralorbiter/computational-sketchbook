import { PlayerEntity } from '../entities/PlayerEntity';
import { HitboxDefinition } from '../../data/moves/MoveDefinition';

export interface ActiveHitbox {
  def: HitboxDefinition;
  attacker: PlayerEntity;
  alreadyHit: Set<PlayerEntity>;
  worldX: number;
  worldY: number;
}

export class HitboxSystem {
  public activeHitboxes: ActiveHitbox[] = [];

  public update(players: PlayerEntity[]) {
    this.activeHitboxes = [];

    for (const player of players) {
      if (player.activeMove && player.movePhase === 'active') {
        const move = player.activeMove;

        // Either create fresh or update existing hitboxes for this move
        // Since we re-generate the array every frame, we need to track alreadyHit across frames.
        // We can attach 'alreadyHit' to the player's active state, or just recreate the list.
        // Wait, if we recreate the list, alreadyHit resets! 
        // We should attach the alreadyHit Set to the player while the move is active.
        
        if (!player.getData('alreadyHitSet')) {
          player.setData('alreadyHitSet', new Set<PlayerEntity>());
        }

        for (const boxDef of move.hitboxes) {
          const dir = player.facingRight ? 1 : -1;
          const hitX = player.x + (boxDef.x * dir);
          const hitY = player.y + boxDef.y;

          this.activeHitboxes.push({
            def: boxDef,
            attacker: player,
            alreadyHit: player.getData('alreadyHitSet'),
            worldX: hitX,
            worldY: hitY,
          });
        }
      } else {
        // Clear history if not active
        if (player.getData('alreadyHitSet')) {
          player.setData('alreadyHitSet', null);
        }
      }
    }
  }
}
