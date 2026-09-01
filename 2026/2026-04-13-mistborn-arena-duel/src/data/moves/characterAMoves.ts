import { MoveDefinition } from './MoveDefinition';

// Light: fast jab, short range
// Heavy: slow push strike with forward momentum
export const characterAMoves: MoveDefinition[] = [
  {
    id: 'charA_light',
    input: 'light',
    startupMs: 80,
    activeMs: 100,
    recoveryMs: 150,
    resourceCost: 0,
    canUseInAir: true,
    hitboxes: [
      {
        x: 30, // Relative to player center. X will be flipped by facing direction natively
        y: -10,
        width: 40,
        height: 20,
        damage: 8,
        knockbackX: 180,
        knockbackY: -100,
        blockstunMs: 120,
        hitstunMs: 250,
      }
    ]
  },
  {
    id: 'charA_heavy',
    input: 'heavy',
    startupMs: 200,
    activeMs: 120,
    recoveryMs: 350,
    resourceCost: 0,
    canUseInAir: false,
    movementImpulse: {
      x: 100, // Move forward during startup
      y: 0
    },
    hitboxes: [
      {
        x: 40,
        y: 0,
        width: 60,
        height: 40,
        damage: 18,
        knockbackX: 380,
        knockbackY: -200,
        blockstunMs: 200,
        hitstunMs: 400,
      }
    ]
  }
];
