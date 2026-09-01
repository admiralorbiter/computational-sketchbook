// Evidence Weave - Grid-based puzzle scene

import Phaser from "phaser";
import { RunManager } from "../systems/RunManager";
import { PuzzleRunner } from "../systems/puzzle/logic/PuzzleRunner";
import { createPuzzleState, createDefaultLevel } from "../systems/puzzle/state/createPuzzleState";
import { GridRenderer } from "../systems/puzzle/view/GridRenderer";
import { PuzzleHud } from "../systems/puzzle/view/PuzzleHud";
import { PlacementController } from "../systems/puzzle/input/PlacementController";
import { getGameState } from "../systems/core/GameState";
import { ChainDetector } from "../systems/puzzle/logic/ChainDetector";
import type { PuzzleState } from "../types/puzzle";

export class NightPuzzleScene extends Phaser.Scene {
  private puzzleRunner!: PuzzleRunner;
  private gridRenderer!: GridRenderer;
  private hud!: PuzzleHud;
  private placementController!: PlacementController;
  private dayIndex = 1;
  private rng!: Phaser.Math.RandomDataGenerator;
  private debugMode = false;
  private debugText!: Phaser.GameObjects.Text;
  private chainDetector!: ChainDetector;

  constructor() {
    super({ key: "NightPuzzleScene" });
  }

  init(data: { dayIndex?: number }) {
    this.dayIndex = data.dayIndex ?? 1;
  }

  create() {
    const { width, height } = this.scale;
    const run = RunManager.ensureRunSeed(this);

    // Initialize RNG with run seed
    this.rng = new Phaser.Math.RandomDataGenerator([run.seed, `puzzle-day-${this.dayIndex}`]);
    
    // Create level definition
    const level = createDefaultLevel(this.dayIndex);
    
    // Create puzzle state
    const initialState = createPuzzleState(level, () => this.rng.frac());
    
    // Initialize puzzle runner
    this.puzzleRunner = new PuzzleRunner(initialState, () => this.rng.frac());
    
    // Initialize chain detector for highlighting
    this.chainDetector = new ChainDetector();
    
    // Setup rendering
    this.cameras.main.setBackgroundColor("#0b0d12");
    this.gridRenderer = new GridRenderer(this);
    this.hud = new PuzzleHud(this);
    
    // Setup input
    this.placementController = new PlacementController(this, this.gridRenderer, this.hud);
    this.placementController.on('handSelected', (handIndex: number) => this.onHandSelected(handIndex));
    this.placementController.on('placementAttempt', (data: { row: number; col: number; tileType: string }) => {
      this.onPlacementAttempt(data.row, data.col, data.tileType as any);
    });
    
    // Initial render
    this.updateDisplay();
    
    // Debug toggle (M key)
    const mKey = this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.M);
    mKey.on('down', () => this.toggleDebug());
    
    // ESC to go back
    const escKey = this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.ESC);
    escKey.on('down', () => {
      this.scene.start("MainMenuScene");
    });
    
    // Debug text (hidden by default)
    this.debugText = this.add.text(16, height - 100, '', {
      fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
      fontSize: '12px',
      color: '#00ff00',
      backgroundColor: '#000000',
      padding: { x: 4, y: 4 }
    }).setVisible(false);
    
    // Cleanup on shutdown
    this.events.on('shutdown', () => {
      this.cleanup();
    });
  }
  
  private onHandSelected(handIndex: number): void {
    const state = this.puzzleRunner.getState();
    if (handIndex >= 0 && handIndex < state.hand.length) {
      const tileType = state.hand[handIndex];
      this.placementController.setSelectedTile(tileType, handIndex);
    } else {
      // Deselect if invalid index
      this.placementController.setSelectedTile(null, -1);
    }
  }
  
  private async onPlacementAttempt(row: number, col: number, tileType: string): Promise<void> {
    const gameState = getGameState();
    const state = gameState.getState();
    
    const result = this.puzzleRunner.attemptPlacement(
      row,
      col,
      tileType as any,
      state.capacity
    );
    
    if (!result.success) {
      // Show invalid feedback (could add visual feedback here)
      console.log('Placement failed:', result.reason);
      return;
    }
    
    // Consume capacity if needed (light integration)
    // This would be handled by PlacementRules, but we need to update GameState
    // For MVP, we'll skip throttle zones for now
    
    // Clear selection
    this.placementController.setSelectedTile(null, -1);
    
    // Update display to show new tile
    this.updateDisplay();
    
    // Get completed chains for animation (before resolving)
    const completedChains = this.puzzleRunner.getCompletedChains();
    
    // Animate chain completions before resolving
    if (completedChains.length > 0) {
      for (const chain of completedChains) {
        await this.gridRenderer.animateChainCompletion(chain);
      }
      // Resolve chains after animation
      await this.puzzleRunner.resolveCompletedChains();
    }
    
    // Run turn (handles taint spread, hand refill, win/loss)
    const turnData = await this.puzzleRunner.runTurn();
    
    // Animate taint events
    if (turnData.taintEvents.length > 0) {
      await this.gridRenderer.animateTaintEvents(turnData.taintEvents);
    }
    
    // Update display after turn
    this.updateDisplay();
    
    // Check for game end
    if (turnData.result.status !== 'continue') {
      await this.handleGameEnd(turnData.result);
    }
  }
  
  private updateDisplay(): void {
    const state = this.puzzleRunner.getState();
    
    // Update grid render
    this.gridRenderer.renderGrid(state);
    
    // Update HUD
    this.hud.updateState(state);
    
    // Highlight valid chains
    this.highlightChains();
    
    // Update debug info
    if (this.debugMode) {
      this.updateDebugInfo();
    }
  }
  
  private highlightChains(): void {
    const state = this.puzzleRunner.getState();
    const chains = this.chainDetector.findAllChains(state.grid);
    const completedChains = chains.filter(chain =>
      this.chainDetector.checkChainCompletion(chain, state.targetPositions)
    );
    
    // Highlight completed chains (ready to resolve)
    if (completedChains.length > 0) {
      const allTiles: Array<{ row: number; col: number }> = [];
      for (const chain of completedChains) {
        allTiles.push(...chain.tiles);
      }
      this.gridRenderer.highlightTiles(allTiles);
    } else {
      // Show potential paths to targets - highlight tiles that could connect
      this.showPathHints(state);
    }
  }
  
  private showPathHints(state: PuzzleState): void {
    // Find tiles that are adjacent to targets or could connect to existing chains
    const hintTiles: Array<{ row: number; col: number }> = [];
    
    // Check each target
    for (const target of state.targetPositions) {
      // Highlight empty cells adjacent to targets
      const directions = [
        { row: -1, col: 0 }, { row: 1, col: 0 },
        { row: 0, col: -1 }, { row: 0, col: 1 }
      ];
      
      for (const dir of directions) {
        const checkRow = target.row + dir.row;
        const checkCol = target.col + dir.col;
        
        if (checkRow >= 0 && checkRow < state.grid.length &&
            checkCol >= 0 && checkCol < state.grid[0].length) {
          const tile = state.grid[checkRow][checkCol];
          if (tile.type === 'empty' && !tile.taintSource) {
            hintTiles.push({ row: checkRow, col: checkCol });
          }
        }
      }
      
      // Also highlight tiles adjacent to existing evidence chains
      const chains = this.chainDetector.findAllChains(state.grid);
      for (const chain of chains) {
        for (const chainTile of chain.tiles) {
          for (const dir of directions) {
            const checkRow = chainTile.row + dir.row;
            const checkCol = chainTile.col + dir.col;
            
            if (checkRow >= 0 && checkRow < state.grid.length &&
                checkCol >= 0 && checkCol < state.grid[0].length) {
              const tile = state.grid[checkRow][checkCol];
              if (tile.type === 'empty' && !tile.taintSource) {
                // Check if this could connect to a target
                const distToTarget = Math.abs(checkRow - target.row) + Math.abs(checkCol - target.col);
                if (distToTarget <= 3) {
                  hintTiles.push({ row: checkRow, col: checkCol });
                }
              }
            }
          }
        }
      }
    }
    
    // Show subtle hints (only if no completed chains)
    if (hintTiles.length > 0 && hintTiles.length < 10) {
      this.gridRenderer.showPathHints(hintTiles);
    }
  }
  
  private async handleGameEnd(turnResult: import('../systems/puzzle/types').TurnResult): Promise<void> {
    const state = this.puzzleRunner.getState();
    
    // Show game over message
    this.hud.showGameOver(
      turnResult.status as 'victory' | 'timeout' | 'corrupted',
      state.evidenceCollected
    );
    
    // Integrate with game state (light integration)
    const gameState = getGameState();
    if (turnResult.reward) {
      // Convert reward to momentum (primary) and standing (small bonus)
      const momentumGain = turnResult.reward;
      const standingGain = Math.floor(turnResult.reward * 0.1);
      
      gameState.updateResources({
        momentum: gameState.getState().momentum + momentumGain,
        standing: gameState.getState().standing + standingGain
      });
    }
    
    // Transition back to day scene after delay
    this.time.delayedCall(3000, () => {
      this.scene.start("DayVNScene", { dayIndex: this.dayIndex + 1 });
    });
  }
  
  private toggleDebug(): void {
    this.debugMode = !this.debugMode;
    this.debugText.setVisible(this.debugMode);
    if (this.debugMode) {
      this.updateDebugInfo();
    }
  }
  
  private updateDebugInfo(): void {
    const state = this.puzzleRunner.getState();
    const chains = this.chainDetector.findAllChains(state.grid);
    
    let debugInfo = `Debug Mode\n`;
    debugInfo += `Chains: ${chains.length}\n`;
    debugInfo += `Taint Sources: ${state.activeTaintSources.length}\n`;
    debugInfo += `Hand: ${state.hand.join(', ')}\n`;
    
    const completedChains = chains.filter(chain =>
      this.chainDetector.checkChainCompletion(chain, state.targetPositions)
    );
    debugInfo += `Completed: ${completedChains.length}\n`;
    
    this.debugText.setText(debugInfo);
  }
  
  private showTutorialIfNeeded(): void {
    const tutorialShown = localStorage.getItem('settlement_tutorial_shown');
    if (tutorialShown === 'true') {
      return; // Already shown
    }
    
    const { width, height } = this.scale;
    
    // Tutorial overlay
    const overlay = this.add.rectangle(width / 2, height / 2, width, height, 0x000000, 0.85);
    const tutorialPanel = this.add.container(width / 2, height / 2);
    
    const panelBg = this.add.rectangle(0, 0, 700, 500, 0x1a1a2e, 1);
    panelBg.setStrokeStyle(3, 0x4a90e2);
    tutorialPanel.add(panelBg);
    
    const title = this.add.text(0, -200, 'HOW TO PLAY', {
      fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
      fontSize: '28px',
      color: '#4a90e2',
      fontWeight: 'bold'
    }).setOrigin(0.5, 0.5);
    tutorialPanel.add(title);
    
    const steps = [
      '🎯 GOAL: Connect evidence tiles to the GREEN targets at the top',
      '',
      '1️⃣ Click a tile in your hand (bottom of screen)',
      '2️⃣ Click an empty grid cell to place it',
      '3️⃣ Connect 3+ tiles in a row/column to form a chain',
      '4️⃣ Chains that reach green targets are completed automatically',
      '5️⃣ Completed chains give you evidence points',
      '',
      '⚠️ WARNING: Red corruption spreads every 2 turns!',
      '   • It spreads to adjacent empty cells',
      '   • It corrupts your evidence tiles (reduces value)',
      '   • Complete chains quickly before they get corrupted!',
      '',
      '💡 TIP: Look for the light blue hints showing good placement spots'
    ];
    
    const tutorialText = this.add.text(0, 0, steps.join('\n'), {
      fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
      fontSize: '16px',
      color: '#b7c3dd',
      align: 'left',
      lineSpacing: 8,
      wordWrap: { width: 650 }
    }).setOrigin(0.5, 0.5);
    tutorialPanel.add(tutorialText);
    
    const closeBtn = this.add.rectangle(0, 200, 200, 50, 0x4a90e2, 1);
    closeBtn.setInteractive({ useHandCursor: true });
    const closeText = this.add.text(0, 200, 'Got it!', {
      fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
      fontSize: '18px',
      color: '#ffffff',
      fontWeight: 'bold'
    }).setOrigin(0.5, 0.5);
    tutorialPanel.add([closeBtn, closeText]);
    
    closeBtn.on('pointerdown', () => {
      overlay.destroy();
      tutorialPanel.destroy();
      localStorage.setItem('settlement_tutorial_shown', 'true');
    });
    
    // Also close on any key press
    const closeKey = this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);
    const closeHandler = () => {
      overlay.destroy();
      tutorialPanel.destroy();
      localStorage.setItem('settlement_tutorial_shown', 'true');
      closeKey.off('down', closeHandler);
    };
    closeKey.on('down', closeHandler);
  }
  
  private cleanup(): void {
    if (this.gridRenderer) {
      this.gridRenderer.destroy();
    }
    if (this.hud) {
      this.hud.destroy();
    }
    if (this.placementController) {
      this.placementController.destroy();
    }
  }
}
