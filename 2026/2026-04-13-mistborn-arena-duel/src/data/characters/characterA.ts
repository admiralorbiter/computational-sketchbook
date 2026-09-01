import { CharacterDefinition } from './CharacterDefinition';
import { characterAMoves } from '../moves/characterAMoves';

export const characterA: CharacterDefinition = {
  id: 'charA',
  displayName: 'Coinshot',
  maxHealth: 100,
  maxResource: 100,
  movement: {
    runSpeed: 300,
    acceleration: 1500,
    deceleration: 1200,
    jumpVelocity: -600,
    airControl: 0.6,
    dashSpeed: 800,
    dashDurationMs: 150,
    dashCooldownMs: 400,
  },
  moves: characterAMoves.map(m => m.id),
  ui: {
    resourceLabel: 'Metals',
  },
};
