import * as Phaser from 'phaser';
import { PlayerEntity } from '../entities/PlayerEntity';
import { HitboxSystem } from '../combat/HitboxSystem';

export class DebugOverlay {
  private p1Text: Phaser.GameObjects.Text;
  private p2Text: Phaser.GameObjects.Text;
  
  public isVisible: boolean;
  public showHitboxes: boolean;
  
  private graphics: Phaser.GameObjects.Graphics;

  constructor(scene: Phaser.Scene) {
    this.isVisible = true;
    this.showHitboxes = false;

    const textStyle = { font: '14px Courier', color: '#00ff00', backgroundColor: '#000000aa' };
    
    this.p1Text = scene.add.text(10, 10, '', textStyle);
    this.p1Text.setScrollFactor(0); // Lock to screen space
    this.p1Text.setDepth(100);

    this.p2Text = scene.add.text(1000, 10, '', textStyle);
    this.p2Text.setScrollFactor(0);
    this.p2Text.setDepth(100);

    this.graphics = scene.add.graphics();
    this.graphics.setDepth(99);

    scene.input.keyboard?.on('keydown-F1', () => {
      this.isVisible = !this.isVisible;
      this.p1Text.setVisible(this.isVisible);
      this.p2Text.setVisible(this.isVisible);
    });

    scene.input.keyboard?.on('keydown-F2', () => {
      this.showHitboxes = !this.showHitboxes;
    });
  }

  public update(p1: PlayerEntity, p2: PlayerEntity, hitboxSystem: HitboxSystem) {
    this.graphics.clear();
    
    // Draw hitboxes and hurtboxes if enabled
    if (this.showHitboxes) {
       this.drawBoxes(p1, p2, hitboxSystem);
    }

    if (!this.isVisible) return;

    this.p1Text.setText([
      '=== PLAYER 1 ===',
      `HP:       ${p1.health} / ${p1.definition.maxHealth}`,
      `State:    ${p1.stateMachine.current}`,
      `Grounded: ${p1.body.blocked.down}`,
      `Move:     ${p1.activeMove ? p1.activeMove.id : 'none'}`,
      `Phase:    ${p1.movePhase || 'none'} (${Math.floor(p1.movePhaseTimerMs)}ms)`,
      `Hitstun:  ${Math.max(0, Math.floor(p1.hitstunTimerMs))}ms`,
      `Hitstop:  ${Math.max(0, Math.floor(p1.hitstopTimerMs))}ms`,
    ]);

    this.p2Text.setText([
      '=== PLAYER 2 ===',
      `HP:       ${p2.health} / ${p2.definition.maxHealth}`,
      `State:    ${p2.stateMachine.current}`,
      `Grounded: ${p2.body.blocked.down}`,
      `Move:     ${p2.activeMove ? p2.activeMove.id : 'none'}`,
      `Phase:    ${p2.movePhase || 'none'} (${Math.floor(p2.movePhaseTimerMs)}ms)`,
      `Hitstun:  ${Math.max(0, Math.floor(p2.hitstunTimerMs))}ms`,
      `Hitstop:  ${Math.max(0, Math.floor(p2.hitstopTimerMs))}ms`,
    ]);
  }

  private drawBoxes(p1: PlayerEntity, p2: PlayerEntity, hitboxSystem: HitboxSystem) {
     this.graphics.lineStyle(2, 0x00ff00, 1);
     this.graphics.strokeRect(p1.x - p1.width/2, p1.y - p1.height/2, p1.width, p1.height);
     this.graphics.strokeRect(p2.x - p2.width/2, p2.y - p2.height/2, p2.width, p2.height);

     this.graphics.fillStyle(0xff0000, 0.5);
     for (const box of hitboxSystem.activeHitboxes) {
        this.graphics.fillRect(
           box.worldX - box.def.width/2,
           box.worldY - box.def.height/2,
           box.def.width,
           box.def.height
        );
     }
  }
}
