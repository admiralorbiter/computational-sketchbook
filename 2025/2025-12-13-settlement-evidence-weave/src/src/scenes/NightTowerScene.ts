// Legacy Contract Tower scene - preserved for reference/debug
// Can be accessed via debug flag if needed

import Phaser from "phaser";
import { RunManager } from "../systems/RunManager";
import { TowerGenerator } from "../puzzle/tower/TowerGenerator";
import { DEFAULT_RULES } from "../puzzle/tower/TowerRules";
import { ContractBlock } from "../puzzle/tower/ContractBlock";

export class NightTowerScene extends Phaser.Scene {
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private player!: MatterJS.BodyType;
  private blocks: MatterJS.BodyType[] = [];
  private debugOn = false;
  private dayIndex = 1;

  constructor() {
    super({ key: "NightTowerScene" });
  }

  init(data: { dayIndex?: number }) {
    this.dayIndex = data.dayIndex ?? 1;
  }

  create() {
    const { width, height } = this.scale;
    const run = RunManager.ensureRunSeed(this);

    // Seed Phaser RNG for procedural tower layout
    const rng = new Phaser.Math.RandomDataGenerator([run.seed, `day-${this.dayIndex}`]);

    // Camera / bounds
    this.matter.world.setBounds(0, 0, width, height);
    this.cameras.main.setBackgroundColor("#0b0d12");

    // HUD
    this.add.text(16, 14, `Night ${this.dayIndex}  •  Seed ${run.seed}`, {
      fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      fontSize: "14px",
      color: "#b7c3dd"
    });

    this.add.text(16, 34, "Move: Arrows / WASD | Push blocks to climb | M: toggle debug | Esc: back", {
      fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      fontSize: "14px",
      color: "#6e7ea3"
    });

    // Ground
    this.matter.add.rectangle(width / 2, height - 18, width, 36, { isStatic: true });

    // Player body (simple circle)
    this.player = this.matter.add.circle(width / 2, height - 80, 18, {
      restitution: 0.0,
      friction: 0.005,
      frictionAir: 0.08
    });

    // Visual for player
    const playerGfx = this.add.graphics();
    playerGfx.fillStyle(0xe8eefc, 1);
    playerGfx.fillCircle(width / 2, height - 80, 18);
    (this.player as any).__settlementPlayerGfx = playerGfx;

    // Build the contract tower
    const gen = new TowerGenerator(this, rng);
    this.blocks = gen.generate(width / 2, height - 120, DEFAULT_RULES);

    // Input
    this.cursors = this.input.keyboard!.createCursorKeys();
    const keys = this.input.keyboard!.addKeys("W,A,S,D,M,ESC") as any;

    keys.M.on("down", () => this.toggleDebug());
    keys.ESC.on("down", () => this.scene.start("MainMenuScene"));

    // Basic win condition: reach a height (top third of screen)
    const winY = height * 0.25;
    const winText = this.add.text(width - 16, 14, "Goal: reach the top", {
      fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      fontSize: "14px",
      color: "#b7c3dd"
    }).setOrigin(1, 0);

    this.events.on("shutdown", () => {
      // clean debug graphics if enabled
      this.matter.world.drawDebug = false;
      this.matter.world.debugGraphic?.clear();
    });

    // Store for update loop
    (this as any).__keys = keys;
    (this as any).__winY = winY;
    (this as any).__winText = winText;
  }

  update() {
    const { height } = this.scale;
    const keys = (this as any).__keys as any;
    const winY = (this as any).__winY as number;
    const winText = (this as any).__winText as Phaser.GameObjects.Text;

    // Player movement: apply forces (keeps Matter feeling but still controllable)
    const speed = 0.0036;
    const jump = 0.018;

    const left = this.cursors.left.isDown || keys.A.isDown;
    const right = this.cursors.right.isDown || keys.D.isDown;
    const up = this.cursors.up.isDown || keys.W.isDown;

    if (left) this.matter.body.applyForce(this.player, this.player.position, { x: -speed, y: 0 });
    if (right) this.matter.body.applyForce(this.player, this.player.position, { x: speed, y: 0 });

    // Jump assist: only if near "ground" or resting on something
    if (up && this.isGrounded()) {
      this.matter.body.applyForce(this.player, this.player.position, { x: 0, y: -jump });
    }

    // Sync player graphics
    const pg: Phaser.GameObjects.Graphics | undefined = (this.player as any).__settlementPlayerGfx;
    if (pg) {
      pg.clear();
      pg.fillStyle(0xe8eefc, 1);
      pg.fillCircle(this.player.position.x, this.player.position.y, 18);
    }

    // Sync block visuals
    for (const b of this.blocks) {
      ContractBlock.syncVisuals(b);
    }

    // Win check
    if (this.player.position.y < winY) {
      winText.setText("Reached the top! → Next day");
      // Advance to next day VN after a short pause
      this.time.delayedCall(600, () => {
        this.scene.start("DayVNScene", { dayIndex: this.dayIndex + 1 });
      });
    } else {
      // Simple lose pressure: if you fall off-screen
      if (this.player.position.y > height + 120) {
        winText.setText("You fell. Try again (new run).");
        this.time.delayedCall(700, () => {
          RunManager.nextRun();
          this.scene.start("NightTowerScene", { dayIndex: this.dayIndex });
        });
      }
    }
  }

  private isGrounded(): boolean {
    // Lightweight grounded check: look for very small vertical velocity OR near bottom.
    // (Later: do proper sensor + collision contacts.)
    const v = (this.player as any).velocity as { x: number; y: number };
    const nearRest = Math.abs(v.y) < 1.2;
    return nearRest;
  }

  private toggleDebug() {
    this.debugOn = !this.debugOn;
    this.matter.world.drawDebug = this.debugOn;
    this.matter.world.debugGraphic?.clear();
  }
}

