"""Type definitions and data models for KC Pathways simulation engine."""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional, List, Dict, Any

TransportProfile = Literal["reliable", "needs-coordination"]
ProvenanceType = Literal["verified_fact", "simulation_assumption", "unknown"]
GameStatus = Literal["playing", "finished"]


@dataclass(frozen=True)
class GameAction:
    """Action that a player can execute within a planning round."""
    id: str
    title: str
    cost_ap: int
    round_available: int
    location_id: str
    result_flag: str
    category: str
    description: str
    outcome_message: str
    requires: List[str] = field(default_factory=list)
    requires_transport_investigation: bool = False
    requires_transport_profile: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GameEvent:
    """Chronological record of an action taken or round milestone reached."""
    round: int
    action_id: str
    action_title: str
    ap_remaining: int
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GameOutcome:
    """Terminal outcome evaluation and educational debrief."""
    id: str
    title: str
    status_badge: str
    description: str
    real_world_takeaway: str
    unanswered_questions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GameState:
    """Full snapshot of an in-progress or completed game run."""
    round: int = 1
    action_points: int = 2
    transport_profile: TransportProfile = "reliable"
    completed_actions: List[str] = field(default_factory=list)
    history: List[GameEvent] = field(default_factory=list)
    status: GameStatus = "playing"
    outcome: Optional[GameOutcome] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "round": self.round,
            "action_points": self.action_points,
            "transport_profile": self.transport_profile,
            "completed_actions": list(self.completed_actions),
            "history": [e.to_dict() for e in self.history],
            "status": self.status,
            "outcome": self.outcome.to_dict() if self.outcome else None,
        }

    def clone(self) -> GameState:
        return GameState(
            round=self.round,
            action_points=self.action_points,
            transport_profile=self.transport_profile,
            completed_actions=list(self.completed_actions),
            history=list(self.history),
            status=self.status,
            outcome=self.outcome,
        )
