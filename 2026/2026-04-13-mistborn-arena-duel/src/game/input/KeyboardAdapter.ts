import * as Phaser from 'phaser';
import { InputAction } from './InputAction';

export interface KeyMap {
  [action: string]: number; // Map InputAction string to Phaser KeyCode
}

export class KeyboardAdapter {
  private keys: Map<InputAction, Phaser.Input.Keyboard.Key> = new Map();

  constructor(scene: Phaser.Scene, keyMap: KeyMap) {
    if (!scene.input.keyboard) {
      throw new Error('Keyboard plugin not available');
    }

    for (const [action, keyCode] of Object.entries(keyMap)) {
      this.keys.set(action as InputAction, scene.input.keyboard.addKey(keyCode));
    }
  }

  public getActiveActions(): Set<InputAction> {
    const active = new Set<InputAction>();
    
    this.keys.forEach((key, action) => {
      if (key.isDown) {
        active.add(action);
      }
    });

    return active;
  }
}
