import { MoveDefinition } from './MoveDefinition';
import { characterAMoves } from './characterAMoves';
import { characterBMoves } from './characterBMoves';

export const MoveRegistry = new Map<string, MoveDefinition>();

[...characterAMoves, ...characterBMoves].forEach(move => {
  MoveRegistry.set(move.id, move);
});

export function getMove(id: string): MoveDefinition {
  const move = MoveRegistry.get(id);
  if (!move) throw new Error(`Move not found: ${id}`);
  return move;
}
