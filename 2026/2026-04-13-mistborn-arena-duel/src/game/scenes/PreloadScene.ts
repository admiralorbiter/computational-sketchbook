import * as Phaser from 'phaser';

export class PreloadScene extends Phaser.Scene {
  constructor() {
    super('PreloadScene');
  }

  preload() {
    // Generate placeholder graphics for Sprint 1
  }

  create() {
    this.scene.start('CombatScene');
  }
}
