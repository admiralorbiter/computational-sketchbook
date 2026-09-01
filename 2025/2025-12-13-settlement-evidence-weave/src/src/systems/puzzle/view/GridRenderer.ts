// Phaser-based grid rendering

import Phaser from 'phaser';
import { PuzzleState, Tile } from '../../types/puzzle';
import { GAME_CONFIG } from '../../../config';

export class GridRenderer {
  private scene: Phaser.Scene;
  private tileSprites: Map<string, Phaser.GameObjects.Rectangle>;
  private highlightSprites: Map<string, Phaser.GameObjects.Rectangle>;
  private hintSprites: Map<string, Phaser.GameObjects.Rectangle>;
  private gridOffsetX: number;
  private gridOffsetY: number;
  
  constructor(scene: Phaser.Scene) {
    this.scene = scene;
    this.tileSprites = new Map();
    this.highlightSprites = new Map();
    this.hintSprites = new Map();
    
    // Center the grid on screen
    const totalWidth = GAME_CONFIG.GRID_COLS * GAME_CONFIG.TILE_SIZE;
    const totalHeight = GAME_CONFIG.GRID_ROWS * GAME_CONFIG.TILE_SIZE;
    this.gridOffsetX = (GAME_CONFIG.WIDTH - totalWidth) / 2;
    this.gridOffsetY = (GAME_CONFIG.HEIGHT - totalHeight) / 2;
  }
  
  /**
   * Convert grid coordinates to screen coordinates
   */
  gridToScreen(row: number, col: number): { x: number; y: number } {
    return {
      x: this.gridOffsetX + col * GAME_CONFIG.TILE_SIZE + GAME_CONFIG.TILE_SIZE / 2,
      y: this.gridOffsetY + row * GAME_CONFIG.TILE_SIZE + GAME_CONFIG.TILE_SIZE / 2
    };
  }
  
  /**
   * Convert screen coordinates to grid coordinates
   */
  screenToGrid(x: number, y: number): { row: number; col: number } | null {
    const col = Math.floor((x - this.gridOffsetX) / GAME_CONFIG.TILE_SIZE);
    const row = Math.floor((y - this.gridOffsetY) / GAME_CONFIG.TILE_SIZE);
    
    if (row >= 0 && row < GAME_CONFIG.GRID_ROWS &&
        col >= 0 && col < GAME_CONFIG.GRID_COLS) {
      return { row, col };
    }
    
    return null;
  }
  
  /**
   * Get color for tile type
   */
  private getTileColor(tile: Tile): number {
    switch (tile.type) {
      case 'evidence':
        return 0x4a90e2; // Blue
      case 'testimony':
        return 0x7b68ee; // Purple
      case 'document':
        return 0xffd700; // Gold
      case 'tainted':
        return 0x8b0000; // Dark red
      case 'blocked':
        return 0x2c2c2c; // Dark gray
      case 'target':
        return 0x00ff00; // Green
      case 'empty':
      default:
        return 0x1a1a2e; // Dark blue-gray
    }
  }
  
  /**
   * Get border color for tile state
   */
  private getBorderColor(tile: Tile): number {
    if (tile.highlighted) {
      return 0xffff00; // Yellow highlight
    }
    if (tile.contested) {
      return 0xff4500; // Orange-red for contested
    }
    if (tile.taintLevel > 0 && tile.type !== 'tainted') {
      return 0xff6347; // Tomato for taint contact
    }
    return 0x444444; // Default gray border
  }
  
  /**
   * Render the entire grid
   */
  renderGrid(state: PuzzleState): void {
    // Clear existing sprites
    this.clearGrid();
    
    for (let row = 0; row < state.grid.length; row++) {
      for (let col = 0; col < state.grid[row].length; col++) {
        const tile = state.grid[row][col];
        this.renderTile(tile);
      }
    }
  }
  
  /**
   * Render a single tile
   */
  private renderTile(tile: Tile): void {
    const key = `${tile.row},${tile.col}`;
    const screenPos = this.gridToScreen(tile.row, tile.col);
    
    // Create or update tile sprite
    let sprite = this.tileSprites.get(key);
    if (!sprite) {
      sprite = this.scene.add.rectangle(
        screenPos.x,
        screenPos.y,
        GAME_CONFIG.TILE_SIZE - 2,
        GAME_CONFIG.TILE_SIZE - 2,
        this.getTileColor(tile),
        1
      );
      sprite.setStrokeStyle(2, this.getBorderColor(tile));
      this.tileSprites.set(key, sprite);
    } else {
      sprite.setFillStyle(this.getTileColor(tile));
      sprite.setStrokeStyle(2, this.getBorderColor(tile));
    }
    
    // Add highlight overlay if needed
    if (tile.highlighted) {
      let highlight = this.highlightSprites.get(key);
      if (!highlight) {
        highlight = this.scene.add.rectangle(
          screenPos.x,
          screenPos.y,
          GAME_CONFIG.TILE_SIZE - 2,
          GAME_CONFIG.TILE_SIZE - 2,
          0xffff00,
          0.3
        );
        this.highlightSprites.set(key, highlight);
      }
    } else {
      const highlight = this.highlightSprites.get(key);
      if (highlight) {
        highlight.destroy();
        this.highlightSprites.delete(key);
      }
    }
  }
  
  /**
   * Highlight specific tiles (for completed chains)
   */
  highlightTiles(positions: Array<{ row: number; col: number }>): void {
    // Clear all highlights and hints first
    this.clearHighlights();
    this.clearHints();
    
    // Add new highlights (bright yellow for completed chains)
    for (const pos of positions) {
      const key = `${pos.row},${pos.col}`;
      const screenPos = this.gridToScreen(pos.row, pos.col);
      
      const highlight = this.scene.add.rectangle(
        screenPos.x,
        screenPos.y,
        GAME_CONFIG.TILE_SIZE - 2,
        GAME_CONFIG.TILE_SIZE - 2,
        0xffff00,
        0.4
      );
      this.highlightSprites.set(key, highlight);
    }
  }
  
  /**
   * Show path hints (subtle indicators for good placement spots)
   */
  showPathHints(positions: Array<{ row: number; col: number }>): void {
    // Clear existing hints
    this.clearHints();
    
    // Add subtle hints (light blue, low opacity)
    for (const pos of positions) {
      const key = `${pos.row},${pos.col}`;
      const screenPos = this.gridToScreen(pos.row, pos.col);
      
      const hint = this.scene.add.rectangle(
        screenPos.x,
        screenPos.y,
        GAME_CONFIG.TILE_SIZE - 4,
        GAME_CONFIG.TILE_SIZE - 4,
        0x4a90e2,
        0.15
      );
      hint.setStrokeStyle(1, 0x4a90e2, 0.3);
      this.hintSprites.set(key, hint);
    }
  }
  
  /**
   * Clear highlight sprites
   */
  private clearHighlights(): void {
    for (const sprite of this.highlightSprites.values()) {
      sprite.destroy();
    }
    this.highlightSprites.clear();
  }
  
  /**
   * Clear hint sprites
   */
  private clearHints(): void {
    for (const sprite of this.hintSprites.values()) {
      sprite.destroy();
    }
    this.hintSprites.clear();
  }
  
  /**
   * Animate chain completion
   */
  async animateChainCompletion(chain: import('../types').Chain): Promise<void> {
    return new Promise((resolve) => {
      const tiles = chain.tiles;
      let completed = 0;
      
      for (const tilePos of tiles) {
        const key = `${tilePos.row},${tilePos.col}`;
        const sprite = this.tileSprites.get(key);
        
        if (sprite) {
          this.scene.tweens.add({
            targets: sprite,
            alpha: 0,
            scaleX: 1.5,
            scaleY: 1.5,
            duration: 300,
            onComplete: () => {
              completed++;
              if (completed === tiles.length) {
                resolve();
              }
            }
          });
        } else {
          completed++;
          if (completed === tiles.length) {
            resolve();
          }
        }
      }
    });
  }
  
  /**
   * Animate taint events
   */
  async animateTaintEvents(events: import('../types').TaintEvent[]): Promise<void> {
    return new Promise((resolve) => {
      if (events.length === 0) {
        resolve();
        return;
      }
      
      let completed = 0;
      
      for (const event of events) {
        const key = `${event.position.row},${event.position.col}`;
        const sprite = this.tileSprites.get(key);
        
        if (sprite) {
          // Pulse animation
          this.scene.tweens.add({
            targets: sprite,
            scaleX: 1.2,
            scaleY: 1.2,
            duration: 150,
            yoyo: true,
            onComplete: () => {
              completed++;
              if (completed === events.length) {
                resolve();
              }
            }
          });
        } else {
          completed++;
          if (completed === events.length) {
            resolve();
          }
        }
      }
    });
  }
  
  /**
   * Clear all grid sprites
   */
  clearGrid(): void {
    for (const sprite of this.tileSprites.values()) {
      sprite.destroy();
    }
    this.tileSprites.clear();
    
    this.clearHighlights();
    this.clearHints();
  }
  
  /**
   * Cleanup on scene shutdown
   */
  destroy(): void {
    this.clearGrid();
  }
}

