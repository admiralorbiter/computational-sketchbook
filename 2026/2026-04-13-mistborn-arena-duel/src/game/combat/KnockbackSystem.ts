import { EventBus } from '../utils/events';

export class KnockbackSystem {
  constructor(private eventBus: EventBus) {
    this.eventBus.on('move_hit', (payload) => {
      const { attacker, defender, hitboxDef } = payload;
      
      // Determine direction of knockback
      const dir = attacker.x < defender.x ? 1 : -1;
      
      defender.body.setVelocity(
        hitboxDef.knockbackX * dir,
        hitboxDef.knockbackY
      );
    });

    this.eventBus.on('block_success', (payload) => {
      const { attacker, defender, hitboxDef } = payload;
      
      const dir = attacker.x < defender.x ? 1 : -1;
      
      // Reduced knockback
      defender.body.setVelocity(
        hitboxDef.knockbackX * 0.5 * dir,
        0 // No air knockback on block usually
      );
    });
  }
}
