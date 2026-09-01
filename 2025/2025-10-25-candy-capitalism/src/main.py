#!/usr/bin/env python3
"""
Candy Capitalism - Main Entry Point

A Halloween-themed economic manipulation game where you play as a market demon
influencing trick-or-treating children to manipulate a candy-based economy.
"""

import sys
import pygame
from src.core.game import Game


def main():
    """Main entry point for the game."""
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except Exception as e:
        print(f"Game crashed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
