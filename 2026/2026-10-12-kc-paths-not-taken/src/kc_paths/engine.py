"""Pure deterministic simulation engine for KC Pathways."""

from typing import List, Dict, Optional
from .types import GameState, GameAction, GameOutcome, GameEvent, TransportProfile
from .data_loader import get_scenario_actions, get_scenario_endings

_DEFAULT_ACTIONS = get_scenario_actions()
_DEFAULT_ENDINGS = get_scenario_endings()


def create_game(transport_profile: TransportProfile = "reliable") -> GameState:
    """Initialize a new game state for Mission 01."""
    if transport_profile not in ("reliable", "needs-coordination"):
        raise ValueError(f"Invalid transport profile: {transport_profile}")
    return GameState(
        round=1,
        action_points=2,
        transport_profile=transport_profile,
        completed_actions=[],
        history=[],
        status="playing",
        outcome=None,
    )


def _get_action_by_id(action_id: str, actions: List[GameAction]) -> Optional[GameAction]:
    for a in actions:
        if a.id == action_id:
            return a
    return None


def _get_completed_flags(state: GameState, actions: List[GameAction]) -> set:
    """Collect all result flags and action IDs completed so far."""
    flags = set(state.completed_actions)
    for a in actions:
        if a.id in state.completed_actions:
            flags.add(a.result_flag)
    return flags


def is_action_unlocked(state: GameState, action: GameAction, actions: List[GameAction] = None) -> bool:
    """Check whether an action's prerequisites and round gates are satisfied."""
    if state.status != "playing":
        return False
    if action.id in state.completed_actions:
        return False
    if state.round < action.round_available:
        return False

    actions = actions or _DEFAULT_ACTIONS
    completed_flags = _get_completed_flags(state, actions)

    # Check required prerequisites
    for req in action.requires:
        if req not in completed_flags and req not in state.completed_actions:
            return False

    # Check transportation profile constraint
    if action.requires_transport_profile and state.transport_profile != action.requires_transport_profile:
        return False

    # Check transportation investigation requirement for Profile B
    if action.requires_transport_investigation and state.transport_profile == "needs-coordination":
        if "transport_documented" not in completed_flags and "investigate_transport" not in state.completed_actions:
            return False

    return True


def can_afford_action(state: GameState, action: GameAction) -> bool:
    """Check if the state has sufficient AP for the action."""
    return state.action_points >= action.cost_ap


def get_available_actions(
    state: GameState,
    affordable_only: bool = True,
    actions: List[GameAction] = None
) -> List[GameAction]:
    """Retrieve all candidate actions for the current state."""
    actions = actions or _DEFAULT_ACTIONS
    available = []
    for a in actions:
        if is_action_unlocked(state, a, actions):
            if not affordable_only or can_afford_action(state, a):
                available.append(a)
    return available


def apply_action(
    state: GameState,
    action_id: str,
    actions: List[GameAction] = None
) -> GameState:
    """Execute an action, decrementing AP and recording completion and event history."""
    if state.status != "playing":
        raise ValueError("Cannot apply action to a finished game.")

    actions = actions or _DEFAULT_ACTIONS
    action = _get_action_by_id(action_id, actions)
    if action is None:
        raise ValueError(f"Unknown action: {action_id}")

    if not is_action_unlocked(state, action, actions):
        raise ValueError(f"Action '{action_id}' is locked or prerequisites are unmet.")

    if not can_afford_action(state, action):
        raise ValueError(
            f"Insufficient action points for '{action.title}': "
            f"needs {action.cost_ap} AP, but only {state.action_points} AP available."
        )

    # Produce pure new state
    new_state = state.clone()
    new_state.action_points -= action.cost_ap
    new_state.completed_actions.append(action.id)

    event = GameEvent(
        round=state.round,
        action_id=action.id,
        action_title=action.title,
        ap_remaining=new_state.action_points,
        message=action.outcome_message,
    )
    new_state.history.append(event)

    return new_state


def advance_round(
    state: GameState,
    endings: Dict[str, GameOutcome] = None
) -> GameState:
    """Advance to the next planning round or conclude the game if Round 3 ends."""
    if state.status == "finished":
        return state

    endings = endings or _DEFAULT_ENDINGS
    new_state = state.clone()

    if new_state.round < 3:
        new_state.round += 1
        new_state.action_points = 2  # Reset AP; unspent points expire
    else:
        new_state.status = "finished"
        new_state.action_points = 0
        new_state.outcome = evaluate_outcome(new_state, endings)

    return new_state


def evaluate_outcome(
    state: GameState,
    endings: Dict[str, GameOutcome] = None
) -> GameOutcome:
    """Evaluate final outcome based on completed actions."""
    endings = endings or _DEFAULT_ENDINGS

    # Priority 1: Health Start inquiry plan
    if "prepare_health_start_inquiry" in state.completed_actions:
        return endings["health_start_prepared"]

    # Priority 2: Postsecondary college exploration plan
    if "draft_postgrad_plan" in state.completed_actions:
        return endings["postgrad_plan_prepared"]

    # Priority 3: Partial exploration
    return endings["still_exploring"]


def run_playthrough(
    actions_by_round: Dict[int, List[str]],
    transport_profile: TransportProfile = "reliable",
    actions: List[GameAction] = None,
    endings: Dict[str, GameOutcome] = None
) -> GameState:
    """Helper to simulate an entire 3-round playthrough."""
    state = create_game(transport_profile=transport_profile)
    for r in range(1, 4):
        round_actions = actions_by_round.get(r, [])
        for act_id in round_actions:
            state = apply_action(state, act_id, actions=actions)
        state = advance_round(state, endings=endings)
    return state
