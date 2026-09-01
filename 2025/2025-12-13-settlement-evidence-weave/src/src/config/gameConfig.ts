import Phaser from "phaser";
import { GAME_CONFIG } from "../config";

export function createGameConfig(): Phaser.Types.Core.GameConfig {
  return {
    type: Phaser.AUTO,
    width: GAME_CONFIG.WIDTH,
    height: GAME_CONFIG.HEIGHT,
    backgroundColor: "#0b0d12",
    pixelArt: false,
    physics: {
      default: "matter",
      matter: {
        gravity: { x: 0, y: 1.25 },
        debug: false
      }
    },
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH
    }
  };
}
