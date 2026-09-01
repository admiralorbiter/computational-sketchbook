// Puzzle HUD/UI overlay

import Phaser from 'phaser';
import { PuzzleState, TileType } from '../../types/puzzle';
import { GAME_CONFIG } from '../../../config';

export class PuzzleHud {
  private scene: Phaser.Scene;
  private turnText!: Phaser.GameObjects.Text;
  private evidenceText!: Phaser.GameObjects.Text;
  private handSprites: Phaser.GameObjects.Rectangle[] = [];
  private handLabels: Phaser.GameObjects.Text[] = [];
  private selectedHandIndex: number = -1;
  private legendText!: Phaser.GameObjects.Text;
  private goalPanel!: Phaser.GameObjects.Container;
  private instructionsText!: Phaser.GameObjects.Text;
  
  constructor(scene: Phaser.Scene) {
    this.scene = scene;
    this.createHud();
  }
  
  private createHud(): void {
    const { width, height } = this.scene.scale;
    
    // Turn counter (top left)
    this.turnText = this.scene.add.text(16, 14, 'Turn: 0', {
      fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
      fontSize: '16px',
      color: '#b7c3dd'
    });
    
    // Evidence counter (top left, below turn)
    this.evidenceText = this.scene.add.text(16, 36, 'Evidence: 0 / 100', {
      fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
      fontSize: '16px',
      color: '#b7c3dd'
    });
    
    // GOAL PANEL - Make it very clear what to do
    this.goalPanel = this.scene.add.container(width / 2, 60);
    const goalBg = this.scene.add.rectangle(0, 0, 600, 80, 0x1a1a2e, 0.9);
    goalBg.setStrokeStyle(2, 0x4a90e2);
    this.goalPanel.add(goalBg);
    
    const goalTitle = this.scene.add.text(0, -25, 'GOAL: Connect Evidence to Green Targets', {
      fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
      fontSize: '18px',
      color: '#4a90e2',
      fontWeight: 'bold',
      align: 'center'
    }).setOrigin(0.5, 0.5);
    this.goalPanel.add(goalTitle);
    
    const goalDesc = this.scene.add.text(0, 5, 
      'Place tiles to form chains of 3+ that TOUCH the green targets (adjacent) at the top',
      {
        fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
        fontSize: '14px',
        color: '#b7c3dd',
        align: 'center',
        wordWrap: { width: 580 }
      }
    ).setOrigin(0.5, 0.5);
    this.goalPanel.add(goalDesc);
    
    // Legend (top right)
    this.legendText = this.scene.add.text(width - 16, 14, 
      'Evidence (Blue)\nTestimony (Purple)\nDocument (Gold)\nTarget (Green)\nTaint (Red)',
      {
        fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
        fontSize: '12px',
        color: '#6e7ea3',
        align: 'right'
      }
    ).setOrigin(1, 0);
    
    // Expanded instructions (bottom)
    this.instructionsText = this.scene.add.text(width / 2, height - 20,
      'HOW TO PLAY:\n1. Click a tile in your hand (below) → 2. Click an empty grid cell to place it\n' +
      '3. Connect 3+ tiles to reach green targets → 4. Complete chains to collect evidence\n' +
      '⚠️ Corruption spreads every 2 turns - complete chains quickly!',
      {
        fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
        fontSize: '12px',
        color: '#b7c3dd',
        align: 'center',
        lineSpacing: 4,
        wordWrap: { width: width - 40 }
      }
    ).setOrigin(0.5, 1);
    
    // Keyboard shortcuts
    this.scene.add.text(width / 2, height - 5,
      'M: Debug | Esc: Back',
      {
        fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
        fontSize: '11px',
        color: '#6e7ea3',
        align: 'center'
      }
    ).setOrigin(0.5, 1);
  }
  
  /**
   * Update HUD with current state
   */
  updateState(state: PuzzleState): void {
    this.turnText.setText(`Turn: ${state.turnsElapsed} / ${state.maxTurns}`);
    this.evidenceText.setText(`Evidence: ${state.evidenceCollected} / ${state.evidenceRequired}`);
    
    this.updateHand(state.hand);
  }
  
  /**
   * Render hand UI
   */
  private updateHand(hand: TileType[]): void {
    const { width, height } = this.scene.scale;
    const handY = height - 100;
    const handStartX = width / 2 - (hand.length * 60) / 2;
    
    // Clear existing hand sprites
    this.clearHand();
    
    for (let i = 0; i < hand.length; i++) {
      const x = handStartX + i * 60;
      const tileType = hand[i];
      
      // Create hand tile sprite
      const color = this.getTileColor(tileType);
      const sprite = this.scene.add.rectangle(x, handY, 50, 50, color, 1);
      sprite.setStrokeStyle(2, i === this.selectedHandIndex ? 0xffff00 : 0x666666);
      sprite.setInteractive({ useHandCursor: true });
      
      // Add label
      const label = this.scene.add.text(x, handY, this.getTileLabel(tileType), {
        fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
        fontSize: '10px',
        color: '#ffffff',
        align: 'center'
      }).setOrigin(0.5, 0.5);
      
      this.handSprites.push(sprite);
      this.handLabels.push(label);
    }
  }
  
  /**
   * Get color for tile type
   */
  private getTileColor(tileType: TileType): number {
    switch (tileType) {
      case 'evidence':
        return 0x4a90e2;
      case 'testimony':
        return 0x7b68ee;
      case 'document':
        return 0xffd700;
      default:
        return 0x1a1a2e;
    }
  }
  
  /**
   * Get short label for tile type
   */
  private getTileLabel(tileType: TileType): string {
    switch (tileType) {
      case 'evidence':
        return 'E';
      case 'testimony':
        return 'T';
      case 'document':
        return 'D';
      default:
        return '?';
    }
  }
  
  /**
   * Set selected hand index
   */
  setSelectedHandIndex(index: number): void {
    this.selectedHandIndex = index;
    
    // Update hand sprites to show selection
    for (let i = 0; i < this.handSprites.length; i++) {
      this.handSprites[i].setStrokeStyle(2, i === index ? 0xffff00 : 0x666666);
    }
  }
  
  /**
   * Get hand sprite at screen position
   */
  getHandIndexAt(x: number, y: number): number {
    for (let i = 0; i < this.handSprites.length; i++) {
      const sprite = this.handSprites[i];
      const bounds = sprite.getBounds();
      if (x >= bounds.x && x <= bounds.x + bounds.width &&
          y >= bounds.y && y <= bounds.y + bounds.height) {
        return i;
      }
    }
    return -1;
  }
  
  /**
   * Clear hand UI
   */
  private clearHand(): void {
    for (const sprite of this.handSprites) {
      sprite.destroy();
    }
    this.handSprites = [];
    
    for (const label of this.handLabels) {
      label.destroy();
    }
    this.handLabels = [];
  }
  
  /**
   * Show game over message
   */
  showGameOver(status: 'victory' | 'timeout' | 'corrupted', evidenceCollected: number): void {
    const { width, height } = this.scene.scale;
    
    let message = '';
    let color = '#b7c3dd';
    
    switch (status) {
      case 'victory':
        message = `Victory! Evidence Collected: ${evidenceCollected}`;
        color = '#00ff00';
        break;
      case 'timeout':
        message = `Time's Up! Evidence Collected: ${evidenceCollected}`;
        color = '#ff6347';
        break;
      case 'corrupted':
        message = `Board Corrupted! Evidence Collected: ${evidenceCollected}`;
        color = '#8b0000';
        break;
    }
    
    const gameOverText = this.scene.add.text(width / 2, height / 2, message, {
      fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
      fontSize: '24px',
      color: color,
      align: 'center'
    }).setOrigin(0.5, 0.5);
    
    // Fade in
    gameOverText.setAlpha(0);
    this.scene.tweens.add({
      targets: gameOverText,
      alpha: 1,
      duration: 500
    });
  }
  
  /**
   * Cleanup
   */
  destroy(): void {
    this.clearHand();
    this.turnText.destroy();
    this.evidenceText.destroy();
    this.legendText.destroy();
  }
}

