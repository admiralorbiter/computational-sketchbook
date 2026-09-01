export interface HitboxDefinition {
  x: number;
  y: number;
  width: number;
  height: number;
  damage: number;
  knockbackX: number;
  knockbackY: number;
  blockstunMs?: number;
  hitstunMs?: number;
}

export interface MoveDefinition {
  id: string;
  input: 'light' | 'heavy' | 'specialNeutral' | 'specialUp' | 'specialDown';
  startupMs: number;
  activeMs: number;
  recoveryMs: number;
  resourceCost: number;
  canUseInAir: boolean;
  movementImpulse?: {
    x: number;
    y: number;
  };
  hitboxes: HitboxDefinition[];
  onHitEffect?: 'knockback' | 'launch' | 'slam';
}
