export type TowerRules = {
  floors: number;
  blocksPerFloor: number;
  ambiguousRate: number; // 0..1
};

export const DEFAULT_RULES: TowerRules = {
  floors: 9,
  blocksPerFloor: 7,
  ambiguousRate: 0.12
};
