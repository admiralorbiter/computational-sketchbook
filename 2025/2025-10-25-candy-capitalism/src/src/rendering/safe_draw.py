"""
Safe drawing helpers for pygame.

Clamps color values, enforces integer coordinates, and guards against
invalid arguments that can cause runtime crashes on some platforms.
"""

from typing import Sequence, Tuple
import pygame


def _clamp_color(color: Sequence[int]) -> Tuple[int, int, int]:
    r = 0 if len(color) < 1 else int(color[0])
    g = 0 if len(color) < 2 else int(color[1])
    b = 0 if len(color) < 3 else int(color[2])
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return (r, g, b)


def circle(surface: pygame.Surface, color: Sequence[int], center, radius: int, width: int = 0):
    try:
        rgb = _clamp_color(color)
        cx = int(center[0])
        cy = int(center[1])
        r = max(0, int(radius))
        w = max(0, int(width))
        pygame.draw.circle(surface, rgb, (cx, cy), r, w)
    except Exception:
        # Silently skip invalid draws to avoid crashing the game loop
        # Consider logging once if needed
        return


def rect(surface: pygame.Surface, color: Sequence[int], rect, width: int = 0):
    try:
        rgb = _clamp_color(color)
        pygame.draw.rect(surface, rgb, rect, max(0, int(width)))
    except Exception:
        return


def line(surface: pygame.Surface, color: Sequence[int], start_pos, end_pos, width: int = 1):
    try:
        rgb = _clamp_color(color)
        pygame.draw.line(surface, rgb, (int(start_pos[0]), int(start_pos[1])), (int(end_pos[0]), int(end_pos[1])), max(1, int(width)))
    except Exception:
        return


def lines(surface: pygame.Surface, color: Sequence[int], closed: bool, points, width: int = 1):
    try:
        rgb = _clamp_color(color)
        int_points = [(int(x), int(y)) for (x, y) in points]
        pygame.draw.lines(surface, rgb, bool(closed), int_points, max(1, int(width)))
    except Exception:
        return


def polygon(surface: pygame.Surface, color: Sequence[int], points, width: int = 0):
    try:
        rgb = _clamp_color(color)
        int_points = [(int(x), int(y)) for (x, y) in points]
        pygame.draw.polygon(surface, rgb, int_points, max(0, int(width)))
    except Exception:
        return


