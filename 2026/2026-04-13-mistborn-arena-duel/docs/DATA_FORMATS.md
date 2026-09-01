# Data Formats

## Character Definition Example

```ts
export interface CharacterDefinition {
  id: string;
  displayName: string;
  maxHealth: number;
  maxResource: number;
  movement: {
    runSpeed: number;
    acceleration: number;
    deceleration: number;
    jumpVelocity: number;
    airControl: number;
    dashSpeed: number;
    dashDurationMs: number;
  };
  moves: string[];
  ui: {
    resourceLabel: string;
  };
}
```

## Move Definition Example

```ts
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
```

## Hitbox Example

```ts
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
```

## Stage Definition Example

```ts
export interface StageDefinition {
  id: string;
  name: string;
  spawnPoints: { x: number; y: number }[];
  anchorPoints: { id: string; x: number; y: number }[];
  bounds: { left: number; right: number; top: number; bottom: number };
}
```
