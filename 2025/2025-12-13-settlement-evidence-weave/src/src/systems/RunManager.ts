import Phaser from "phaser";

type RunState = {
  seed: string;
  runNumber: number;
};

const KEY = "settlement_run_state_v1";

export class RunManager {
  static ensureRunSeed(scene: Phaser.Scene): RunState {
    const existing = this.load();
    if (existing) return existing;

    const seed = `${Date.now()}-${Math.floor(Math.random() * 1e9)}`;
    const state: RunState = { seed, runNumber: 1 };
    this.save(state);
    return state;
  }

  static nextRun(): RunState {
    const existing = this.load() ?? { seed: "0", runNumber: 0 };
    const seed = `${Date.now()}-${Math.floor(Math.random() * 1e9)}`;
    const state: RunState = { seed, runNumber: existing.runNumber + 1 };
    this.save(state);
    return state;
  }

  static load(): RunState | null {
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return null;
      return JSON.parse(raw) as RunState;
    } catch {
      return null;
    }
  }

  static save(state: RunState) {
    localStorage.setItem(KEY, JSON.stringify(state));
  }

  static reset() {
    localStorage.removeItem(KEY);
  }
}
