"""Data loaders and validators for KC Pathways dataset records."""

import json
from pathlib import Path
from typing import Dict, Any, List
from .types import GameAction, GameOutcome

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def load_locations(data_path: Path = None) -> Dict[str, Any]:
    """Load verified GeoJSON locations."""
    path = data_path or (DATA_DIR / "locations.geojson")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_programs(data_path: Path = None) -> Dict[str, Any]:
    """Load verified programs dictionary."""
    path = data_path or (DATA_DIR / "programs.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sources(data_path: Path = None) -> Dict[str, Any]:
    """Load source verification registry."""
    path = data_path or (DATA_DIR / "sources.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_scenario(data_path: Path = None) -> Dict[str, Any]:
    """Load raw scenario configuration."""
    path = data_path or (DATA_DIR / "scenarios.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_scenario_actions(data_path: Path = None) -> List[GameAction]:
    """Load scenario actions as typed GameAction objects."""
    raw = load_scenario(data_path)
    actions_raw = raw["scenario"]["actions"]
    actions = []
    for a in actions_raw:
        actions.append(
            GameAction(
                id=a["id"],
                title=a["title"],
                cost_ap=a["cost_ap"],
                round_available=a["round_available"],
                location_id=a["location_id"],
                result_flag=a["result_flag"],
                category=a["category"],
                description=a["description"],
                outcome_message=a["outcome_message"],
                requires=a.get("requires", []),
                requires_transport_investigation=a.get("requires_transport_investigation", False),
                requires_transport_profile=a.get("requires_transport_profile"),
            )
        )
    return actions


def get_scenario_endings(data_path: Path = None) -> Dict[str, GameOutcome]:
    """Load scenario endings as typed GameOutcome objects."""
    raw = load_scenario(data_path)
    endings_raw = raw["scenario"]["endings"]
    endings = {}
    for eid, e in endings_raw.items():
        endings[eid] = GameOutcome(
            id=e["id"],
            title=e["title"],
            status_badge=e["status_badge"],
            description=e["description"],
            real_world_takeaway=e["real_world_takeaway"],
            unanswered_questions=e["unanswered_questions"],
        )
    return endings
