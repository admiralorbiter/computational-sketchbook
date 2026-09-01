import * as Phaser from 'phaser';
import { BootScene } from '../game/scenes/BootScene';
import { PreloadScene } from '../game/scenes/PreloadScene';
import { CombatScene } from '../game/scenes/CombatScene';
import { debugConfig } from './debugConfig';

export const gameConfig: Phaser.Types.Core.GameConfig = {
  type: Phaser.WEBGL,
  width: 1280,
  height: 720,
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { x: 0, y: 900 },
      debug: debugConfig.showPhysics,
    },
  },
  scene: [BootScene, PreloadScene, CombatScene],
  backgroundColor: '#1a1a2e',
};
