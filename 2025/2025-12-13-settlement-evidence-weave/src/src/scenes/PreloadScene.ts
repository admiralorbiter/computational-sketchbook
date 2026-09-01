import Phaser from "phaser";

export class PreloadScene extends Phaser.Scene {
  constructor() {
    super({ key: "PreloadScene" });
  }

  preload() {
    // Replace these with real art later.
    // For now, we just show a simple progress bar.
    const { width, height } = this.scale;
    const bar = this.add.rectangle(width / 2, height / 2, 0, 12, 0x6aa6ff).setOrigin(0.5);
    this.load.on("progress", (p: number) => {
      bar.width = Math.floor((width * 0.6) * p);
    });

    // Example: this.load.image("portrait", "assets/portrait.png");
  }

  create() {
    this.scene.start("MainMenuScene");
  }
}
