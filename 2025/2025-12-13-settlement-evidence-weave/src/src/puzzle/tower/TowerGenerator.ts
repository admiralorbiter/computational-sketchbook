import Phaser from "phaser";
import { ClauseType } from "./ClauseTypes";
import { ContractBlock, ContractBlockSpec } from "./ContractBlock";
import { TowerRules } from "./TowerRules";

const BASE_CLAUSES: ClauseType[] = ["IF", "THEN", "AND", "OR", "DEADLINE", "EVIDENCE", "AUDIT"];

export class TowerGenerator {
  constructor(private scene: Phaser.Scene, private rng: Phaser.Math.RandomDataGenerator) {}

  generate(originX: number, floorY: number, rules: TowerRules) {
    const blocks: MatterJS.BodyType[] = [];

    const blockW = 110;
    const blockH = 34;
    const gapX = 14;

    for (let floor = 0; floor < rules.floors; floor++) {
      const y = floorY - floor * 58;

      for (let i = 0; i < rules.blocksPerFloor; i++) {
        const x = originX + (i - (rules.blocksPerFloor - 1) / 2) * (blockW + gapX);

        const isAmb = this.rng.frac() < rules.ambiguousRate;
        const clause = isAmb ? ("AMBIGUOUS" as const) : (this.pickClause() as ClauseType);

        const spec: ContractBlockSpec = {
          clause,
          label: isAmb ? "AMBIG" : clause,
          isFragile: isAmb
        };

        const cb = new ContractBlock(this.scene, x, y, blockW, blockH, spec);
        blocks.push(cb.body);
      }
    }

    return blocks;
  }

  private pickClause(): ClauseType {
    const idx = Math.floor(this.rng.frac() * BASE_CLAUSES.length);
    return BASE_CLAUSES[idx];
  }
}
