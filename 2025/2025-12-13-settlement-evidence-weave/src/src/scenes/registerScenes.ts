import Phaser from "phaser";
import { BootScene } from "./BootScene";
import { PreloadScene } from "./PreloadScene";
import { MainMenuScene } from "./MainMenuScene";
import { DayVNScene } from "./DayVNScene";
import { NightPuzzleScene } from "./NightPuzzleScene";
import { NightTowerScene } from "./NightTowerScene";

export function registerScenes(config: Phaser.Types.Core.GameConfig) {
  // Order matters: Boot -> Preload -> MainMenu
  config.scene = [BootScene, PreloadScene, MainMenuScene, DayVNScene, NightPuzzleScene, NightTowerScene];
}
