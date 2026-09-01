import { PlayerEntity } from '../entities/PlayerEntity';
import { HitboxDefinition } from '../../data/moves/MoveDefinition';

export type GameEventType =
  | 'move_started'
  | 'move_hit'
  | 'block_success'
  | 'hitstun_started'
  | 'player_ko';

export interface MoveHitPayload {
  attacker: PlayerEntity;
  defender: PlayerEntity;
  hitboxDef: HitboxDefinition;
}

export interface BlockSuccessPayload {
  attacker: PlayerEntity;
  defender: PlayerEntity;
  hitboxDef: HitboxDefinition;
}

type EventMap = {
  'move_started': { player: PlayerEntity };
  'move_hit': MoveHitPayload;
  'block_success': BlockSuccessPayload;
  'hitstun_started': { player: PlayerEntity; durationMs: number };
  'player_ko': { player: PlayerEntity };
};

export class EventBus {
  private readonly listeners: { [K in keyof EventMap]?: Array<(payload: EventMap[K]) => void> } = {};

  public on<K extends keyof EventMap>(event: K, callback: (payload: EventMap[K]) => void) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event]!.push(callback);
  }

  public emit<K extends keyof EventMap>(event: K, payload: EventMap[K]) {
    if (this.listeners[event]) {
      for (const listener of this.listeners[event]!) {
        listener(payload);
      }
    }
  }
}
