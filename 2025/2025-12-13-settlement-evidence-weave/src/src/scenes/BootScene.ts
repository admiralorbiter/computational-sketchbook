import Phaser from "phaser";

export class BootScene extends Phaser.Scene {
  constructor() {
    super({ key: "BootScene" });
  }

  create() {
    // Any minimal setup (input, scale, etc.) can go here.
    this.scene.start("PreloadScene");
  }
}
