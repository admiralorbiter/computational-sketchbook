import * as Phaser from 'phaser';
import { KeyboardAdapter, KeyMap } from './KeyboardAdapter';
import { InputFrame } from './InputFrame';

export class InputManager {
  private readonly adapters: KeyboardAdapter[] = [];
  
  private currentFrames: InputFrame[] = [
    { actions: new Set(), timestamp: 0 },
    { actions: new Set(), timestamp: 0 },
  ];

  private previousFrames: InputFrame[] = [
    { actions: new Set(), timestamp: 0 },
    { actions: new Set(), timestamp: 0 },
  ];

  constructor(scene: Phaser.Scene) {
    const p1Map: KeyMap = {
      moveLeft: Phaser.Input.Keyboard.KeyCodes.A,
      moveRight: Phaser.Input.Keyboard.KeyCodes.D,
      jump: Phaser.Input.Keyboard.KeyCodes.W,
      dash: Phaser.Input.Keyboard.KeyCodes.SHIFT,
      light: Phaser.Input.Keyboard.KeyCodes.J,
      heavy: Phaser.Input.Keyboard.KeyCodes.K,
      block: Phaser.Input.Keyboard.KeyCodes.L,
    };

    const p2Map: KeyMap = {
      moveLeft: Phaser.Input.Keyboard.KeyCodes.LEFT,
      moveRight: Phaser.Input.Keyboard.KeyCodes.RIGHT,
      jump: Phaser.Input.Keyboard.KeyCodes.UP,
      dash: Phaser.Input.Keyboard.KeyCodes.CTRL,
      light: Phaser.Input.Keyboard.KeyCodes.COMMA,
      heavy: Phaser.Input.Keyboard.KeyCodes.PERIOD,
      block: Phaser.Input.Keyboard.KeyCodes.FORWARD_SLASH,
    };

    this.adapters.push(new KeyboardAdapter(scene, p1Map));
    this.adapters.push(new KeyboardAdapter(scene, p2Map));
  }

  public update(time: number) {
    this.previousFrames = [...this.currentFrames];
    
    this.currentFrames = this.adapters.map(adapter => ({
      actions: adapter.getActiveActions(),
      timestamp: time
    }));
  }

  public getFrame(playerIndex: 0 | 1): InputFrame {
    return this.currentFrames[playerIndex];
  }

  public getPreviousFrame(playerIndex: 0 | 1): InputFrame {
    return this.previousFrames[playerIndex];
  }
}
