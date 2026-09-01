import { MoveDefinition } from './MoveDefinition';

// Light: medium speed poke
// Heavy: high damage sluggish sweep
export const characterBMoves: MoveDefinition[] = [
  {
    id: 'charB_light',
    input: 'light',
    startupMs: 90,
    activeMs: 90,
    recoveryMs: 140,
    resourceCost: 0,
    canUseInAir: true,
    hitboxes: [
      {
        x: 35,
        y: 10,
        width: 30,
        height: 20,
        damage: 9,
        knockbackX: 200,
        knockbackY: -80,
        blockstunMs: 130,
        hitstunMs: 260,
      }
    ]
  },
  {
    id: 'charB_heavy',
    input: 'heavy',
    startupMs: 180,
    activeMs: 140,
    recoveryMs: 300,
    resourceCost: 0,
    canUseInAir: false,
    hitboxes: [
      {
        x: 45,
        y: 20,
        width: 70,
        height: 30,
        damage: 20,
        knockbackX: 350,
        knockbackY: -250,
        blockstunMs: 250,
        hitstunMs: 450,
      }
    ]
  }
];
