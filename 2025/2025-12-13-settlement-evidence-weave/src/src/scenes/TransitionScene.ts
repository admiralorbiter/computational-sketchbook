import Phaser from "phaser";

/**
 * Transition scene for smooth transitions between major game phases.
 * Can be used for day/night transitions, scene fades, etc.
 */
export class TransitionScene extends Phaser.Scene {
  constructor() {
    super({ key: "TransitionScene" });
  }

  init(data: { 
    from?: string;
    to?: string;
    duration?: number;
    fadeColor?: number;
  }) {
    // Transition parameters can be passed via init data
    (this as any).__transitionData = {
      from: data.from ?? "",
      to: data.to ?? "",
      duration: data.duration ?? 500,
      fadeColor: data.fadeColor ?? 0x000000,
    };
  }

  create() {
    const { width, height } = this.scale;
    const data = (this as any).__transitionData;

    // Create fade overlay
    const overlay = this.add.rectangle(width / 2, height / 2, width, height, data.fadeColor, 0);
    
    // Fade in
    this.tweens.add({
      targets: overlay,
      alpha: 1,
      duration: data.duration / 2,
      onComplete: () => {
        // Transition to target scene
        if (data.to) {
          this.scene.start(data.to);
        } else {
          // If no target, just fade out and return
          this.tweens.add({
            targets: overlay,
            alpha: 0,
            duration: data.duration / 2,
            onComplete: () => {
              this.scene.stop();
            }
          });
        }
      }
    });
  }
}

