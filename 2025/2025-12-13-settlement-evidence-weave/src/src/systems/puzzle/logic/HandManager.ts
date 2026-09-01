// Pure hand management logic - no Phaser dependencies

import { TileType } from '../../types/puzzle';

export interface HandWeights {
  evidence: number;
  testimony: number;
  document: number;
}

export class HandManager {
  private readonly DEFAULT_WEIGHTS: HandWeights = {
    evidence: 40,    // Most common
    testimony: 40,   // Most common
    document: 20     // Rarer, higher value
  };
  
  /**
   * Generate a weighted random tile type
   */
  private generateTileType(rng: () => number, weights: HandWeights = this.DEFAULT_WEIGHTS): TileType {
    const total = weights.evidence + weights.testimony + weights.document;
    const roll = rng() * total;
    
    if (roll < weights.evidence) {
      return 'evidence';
    } else if (roll < weights.evidence + weights.testimony) {
      return 'testimony';
    } else {
      return 'document';
    }
  }
  
  /**
   * Refill hand to target size
   */
  refillHand(
    currentHand: TileType[],
    targetSize: number,
    rng: () => number,
    weights?: HandWeights
  ): TileType[] {
    const newHand = [...currentHand];
    
    while (newHand.length < targetSize) {
      newHand.push(this.generateTileType(rng, weights));
    }
    
    return newHand;
  }
  
  /**
   * Remove a tile from hand (by type, removes first match)
   */
  removeFromHand(hand: TileType[], tileType: TileType): TileType[] {
    const index = hand.indexOf(tileType);
    if (index === -1) {
      return hand; // Not found, return unchanged
    }
    
    const newHand = [...hand];
    newHand.splice(index, 1);
    return newHand;
  }
}

