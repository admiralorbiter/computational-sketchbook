// Input handling for tile placement

import Phaser from 'phaser';
import { TileType } from '../../types/puzzle';
import { GridRenderer } from '../view/GridRenderer';
import { PuzzleHud } from '../view/PuzzleHud';

export class PlacementController extends Phaser.Events.EventEmitter {
  private scene: Phaser.Scene;
  private gridRenderer: GridRenderer;
  private hud: PuzzleHud;
  private selectedTile: TileType | null = null;
  private previewSprite: Phaser.GameObjects.Rectangle | null = null;
  
  constructor(scene: Phaser.Scene, gridRenderer: GridRenderer, hud: PuzzleHud) {
    super();
    this.scene = scene;
    this.gridRenderer = gridRenderer;
    this.hud = hud;
    this.setupInput();
  }
  
  private setupInput(): void {
    // Pointer down - select from hand or place on grid
    this.scene.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      // Check if clicking on hand
      const handIndex = this.hud.getHandIndexAt(pointer.x, pointer.y);
      if (handIndex !== -1) {
        // Get hand from current state (we'll need to pass this)
        // For now, we'll emit an event and let the scene handle it
        this.emit('handSelected', handIndex);
        return;
      }
      
      // Check if clicking on grid
      const gridPos = this.gridRenderer.screenToGrid(pointer.x, pointer.y);
      if (gridPos && this.selectedTile) {
        this.emit('placementAttempt', {
          row: gridPos.row,
          col: gridPos.col,
          tileType: this.selectedTile
        });
      }
    });
    
    // Pointer move - update preview
    this.scene.input.on('pointermove', (pointer: Phaser.Input.Pointer) => {
      if (this.selectedTile) {
        this.updatePreview(pointer.x, pointer.y);
      }
    });
    
    // Keyboard - ESC to cancel selection
    const escKey = this.scene.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.ESC);
    escKey.on('down', () => {
      this.clearSelection();
    });
  }
  
  /**
   * Set selected tile from hand
   */
  setSelectedTile(tileType: TileType | null, handIndex: number = -1): void {
    this.selectedTile = tileType;
    this.hud.setSelectedHandIndex(handIndex);
    
    if (!tileType) {
      this.clearPreview();
    }
  }
  
  /**
   * Update preview sprite position
   */
  private updatePreview(x: number, y: number): void {
    const gridPos = this.gridRenderer.screenToGrid(x, y);
    
    if (!gridPos) {
      this.clearPreview();
      return;
    }
    
    const screenPos = this.gridRenderer.gridToScreen(gridPos.row, gridPos.col);
    
    if (!this.previewSprite) {
      this.previewSprite = this.scene.add.rectangle(
        screenPos.x,
        screenPos.y,
        48,
        48,
        0xffffff,
        0.3
      );
      this.previewSprite.setStrokeStyle(2, 0xffff00);
    } else {
      this.previewSprite.setPosition(screenPos.x, screenPos.y);
    }
  }
  
  /**
   * Clear preview sprite
   */
  private clearPreview(): void {
    if (this.previewSprite) {
      this.previewSprite.destroy();
      this.previewSprite = null;
    }
  }
  
  /**
   * Clear selection
   */
  private clearSelection(): void {
    this.selectedTile = null;
    this.hud.setSelectedHandIndex(-1);
    this.clearPreview();
  }
  
  /**
   * Cleanup
   */
  destroy(): void {
    this.clearPreview();
    this.removeAllListeners();
  }
}

