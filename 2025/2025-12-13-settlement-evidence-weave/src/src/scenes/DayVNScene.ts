    import Phaser from "phaser";
    import { RunManager } from "../systems/RunManager";

    export class DayVNScene extends Phaser.Scene {
      private dayIndex = 1;

      constructor() {
        super({ key: "DayVNScene" });
      }

      init(data: { dayIndex?: number }) {
        this.dayIndex = data.dayIndex ?? 1;
      }

      create() {
        const { width, height } = this.scale;

        RunManager.ensureRunSeed(this);

        this.add.rectangle(width / 2, height / 2, width, height, 0x0b0d12, 1);

        this.add.text(width / 2, height * 0.2, `Day ${this.dayIndex}`, {
          fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
          fontSize: "34px",
          color: "#e8eefc"
        }).setOrigin(0.5);

        this.add.text(width / 2, height * 0.34,
          `Placeholder VN scene.
You'll eventually load dialogue, choices, and markets here.`,
          {
            align: "center",
            fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
            fontSize: "18px",
            color: "#b7c3dd",
            lineSpacing: 6
          }
        ).setOrigin(0.5);

        const btn = this.add.rectangle(width / 2, height * 0.72, 320, 54, 0x1e2a44, 1)
          .setStrokeStyle(2, 0x6aa6ff)
          .setInteractive({ useHandCursor: true });

        this.add.text(width / 2, height * 0.72, "Go to Night Puzzle", {
          fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
          fontSize: "20px",
          color: "#e8eefc"
        }).setOrigin(0.5);

        btn.on("pointerup", () => {
          this.scene.start("NightPuzzleScene", { dayIndex: this.dayIndex });
        });
      }
    }
