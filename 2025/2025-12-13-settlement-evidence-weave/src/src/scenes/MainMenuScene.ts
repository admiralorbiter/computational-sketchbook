import Phaser from "phaser";

export class MainMenuScene extends Phaser.Scene {
  constructor() {
    super({ key: "MainMenuScene" });
  }

  create() {
    const { width, height } = this.scale;

    this.add.text(width / 2, height * 0.28, "SETTLEMENT", {
      fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      fontSize: "48px",
      color: "#e8eefc"
    }).setOrigin(0.5);

    this.add.text(width / 2, height * 0.42, "VN by day. Contract Tower by night.", {
      fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      fontSize: "18px",
      color: "#b7c3dd"
    }).setOrigin(0.5);

    const btn = this.add.rectangle(width / 2, height * 0.62, 260, 54, 0x1e2a44, 1)
      .setStrokeStyle(2, 0x6aa6ff)
      .setInteractive({ useHandCursor: true });

    this.add.text(width / 2, height * 0.62, "Start Run", {
      fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      fontSize: "20px",
      color: "#e8eefc"
    }).setOrigin(0.5);

    btn.on("pointerup", () => {
      // Start daytime VN first (stub), which then leads into the puzzle.
      this.scene.start("DayVNScene", { dayIndex: 1 });
    });

    this.add.text(width / 2, height * 0.82, "Tip: press M in puzzle to toggle Matter debug.", {
      fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      fontSize: "14px",
      color: "#6e7ea3"
    }).setOrigin(0.5);
  }
}
