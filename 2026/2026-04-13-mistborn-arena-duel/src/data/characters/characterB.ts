import { CharacterDefinition } from './CharacterDefinition';
import { characterBMoves } from '../moves/characterBMoves';

export const characterB: CharacterDefinition = {
  id: 'charB',
  displayName: 'Lurcher',
  maxHealth: 120, // slightly more health
  maxResource: 100,
  movement: {
    runSpeed: 270, // slightly slower
    acceleration: 1200,
    deceleration: 1000,
    jumpVelocity: -580,
    airControl: 0.5,
    dashSpeed: 700,
    dashDurationMs: 180, // longer dash
    dashCooldownMs: 500,
  },
  moves: characterBMoves.map(m => m.id),
  ui: {
    resourceLabel: 'Metals',
  },
};
