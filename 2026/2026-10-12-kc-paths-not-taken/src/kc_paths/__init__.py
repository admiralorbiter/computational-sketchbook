"""KC Pathways: A data-driven exploration game about education, careers, geography, and opportunity in Kansas City."""

from .types import GameState, TransportProfile, GameAction, GameOutcome, ProvenanceType
from .engine import (
    create_game,
    get_available_actions,
    can_afford_action,
    apply_action,
    advance_round,
    evaluate_outcome,
    run_playthrough
)
from .data_loader import load_locations, load_programs, load_sources, load_scenario
from .widget import render_playable_game

__all__ = [
    "GameState",
    "TransportProfile",
    "GameAction",
    "GameOutcome",
    "ProvenanceType",
    "create_game",
    "get_available_actions",
    "can_afford_action",
    "apply_action",
    "advance_round",
    "evaluate_outcome",
    "run_playthrough",
    "load_locations",
    "load_programs",
    "load_sources",
    "load_scenario",
    "render_playable_game",
]
