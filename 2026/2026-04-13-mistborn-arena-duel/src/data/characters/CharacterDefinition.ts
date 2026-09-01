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
    dashCooldownMs: number;
  };
  moves: string[];
  ui: {
    resourceLabel: string;
  };
}

export const placeholderCharacter: CharacterDefinition = {
  id: 'placeholder',
  displayName: 'Placeholder',
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
  moves: [],
  ui: {
    resourceLabel: 'Energy',
  },
};
