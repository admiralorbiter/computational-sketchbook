"""Unit tests for the KC Pathways deterministic simulation engine and data integrity."""

import pytest
import sys
from pathlib import Path

# Ensure src is on sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from kc_paths.engine import (
    create_game,
    get_available_actions,
    can_afford_action,
    apply_action,
    advance_round,
    evaluate_outcome,
    run_playthrough,
)
from kc_paths.data_loader import (
    load_locations,
    load_programs,
    load_sources,
    load_scenario,
    get_scenario_actions,
    get_scenario_endings,
)


class TestKCPathwaysEngine:

    def test_initial_state_defaults(self):
        state = create_game("reliable")
        assert state.round == 1
        assert state.action_points == 2
        assert state.transport_profile == "reliable"
        assert state.completed_actions == []
        assert state.status == "playing"
        assert state.outcome is None

    def test_action_costs_1_ap(self):
        state = create_game("reliable")
        state = apply_action(state, "speak_counselor")
        assert state.action_points == 1
        assert "speak_counselor" in state.completed_actions
        assert len(state.history) == 1
        assert state.history[0].action_id == "speak_counselor"

    def test_action_costs_2_ap_insufficient_ap(self):
        state = create_game("reliable")
        # Complete prerequisites for prepare_health_start_inquiry
        state = apply_action(state, "speak_counselor")  # 1 AP left
        state = advance_round(state)                     # Round 2: 2 AP
        state = apply_action(state, "investigate_health_start") # 1 AP left

        # prepare_health_start_inquiry costs 2 AP, but state only has 1 AP
        available = get_available_actions(state, affordable_only=True)
        assert "prepare_health_start_inquiry" not in [a.id for a in available]

        # Explicitly trying to apply it raises ValueError
        with pytest.raises(ValueError, match="Insufficient action points"):
            apply_action(state, "prepare_health_start_inquiry")

    def test_duplicate_action_rejected(self):
        state = create_game("reliable")
        state = apply_action(state, "speak_counselor")
        with pytest.raises(ValueError, match="locked or prerequisites are unmet"):
            apply_action(state, "speak_counselor")

    def test_prerequisites_enforced(self):
        state = create_game("reliable")
        # Attempt to prepare Health Start inquiry without counselor or research
        available = get_available_actions(state, affordable_only=False)
        assert "prepare_health_start_inquiry" not in [a.id for a in available]

        with pytest.raises(ValueError, match="locked or prerequisites are unmet"):
            apply_action(state, "prepare_health_start_inquiry")

    def test_transportation_coordination_enforced(self):
        # In 'needs-coordination' mode, prepare_health_start_inquiry requires investigate_transport
        state = create_game("needs-coordination")
        state = apply_action(state, "speak_counselor")
        state = advance_round(state)  # Round 2
        state = apply_action(state, "investigate_health_start")
        state = advance_round(state)  # Round 3: 2 AP

        # Has counselor + research, but lacks transport investigation
        available = get_available_actions(state, affordable_only=False)
        assert "prepare_health_start_inquiry" not in [a.id for a in available]

        with pytest.raises(ValueError, match="locked or prerequisites are unmet"):
            apply_action(state, "prepare_health_start_inquiry")

    def test_health_start_pathway_reliable(self):
        """Full successful run for Health Start with reliable transport."""
        playthrough = {
            1: ["speak_counselor", "investigate_health_start"],  # 2 AP spent
            2: ["prepare_health_start_inquiry"],                 # 2 AP spent
            3: ["explore_mcc_health", "compare_college_options"] # 2 AP spent
        }
        state = run_playthrough(playthrough, transport_profile="reliable")
        assert state.status == "finished"
        assert state.outcome is not None
        assert state.outcome.id == "health_start_prepared"

    def test_health_start_pathway_with_coordination(self):
        """Full successful run for Health Start with transport coordination."""
        playthrough = {
            1: ["speak_counselor", "investigate_health_start"],  # 2 AP spent
            2: ["investigate_transport", "explore_mcc_health"],  # 2 AP spent (investigates transport + explores)
            3: ["prepare_health_start_inquiry"],                 # 2 AP spent -> completes plan!
        }
        state = run_playthrough(playthrough, transport_profile="needs-coordination")
        assert state.status == "finished"
        assert state.outcome is not None
        assert state.outcome.id == "health_start_prepared"

    def test_postsecondary_mcc_pathway(self):
        """Full successful run for MCC postsecondary college pathway."""
        playthrough = {
            1: ["speak_counselor", "investigate_health_start"],
            2: ["explore_mcc_health", "compare_college_options"],
            3: ["draft_postgrad_plan"]  # Leaves 1 AP unspent
        }
        state = run_playthrough(playthrough, transport_profile="reliable")
        assert state.status == "finished"
        assert state.outcome is not None
        assert state.outcome.id == "postgrad_plan_prepared"

    def test_still_exploring_ending(self):
        """Player spends points on disconnected tasks without completing a terminal plan."""
        playthrough = {
            1: ["speak_counselor"],            # 1 AP unspent
            2: ["explore_mcc_health"],          # 1 AP unspent
            3: ["compare_college_options"]      # 1 AP unspent
        }
        state = run_playthrough(playthrough, transport_profile="reliable")
        assert state.status == "finished"
        assert state.outcome is not None
        assert state.outcome.id == "still_exploring"

    def test_unspent_ap_expires_at_round_boundary(self):
        state = create_game("reliable")
        state = apply_action(state, "speak_counselor")  # 1 AP remaining
        state = advance_round(state)                     # Advance to Round 2
        assert state.round == 2
        # AP resets to 2, does NOT accumulate to 3
        assert state.action_points == 2

    def test_round_temporal_gate(self):
        state = create_game("reliable")
        # In Round 1, explore_mcc_health is not unlocked because round_available == 2
        available = get_available_actions(state, affordable_only=False)
        assert "explore_mcc_health" not in [a.id for a in available]

        state = advance_round(state) # Round 2
        available = get_available_actions(state, affordable_only=False)
        assert "explore_mcc_health" in [a.id for a in available]

    def test_replay_clean_state(self):
        state1 = run_playthrough({1: ["speak_counselor", "investigate_health_start"]}, "reliable")
        state2 = create_game("needs-coordination")
        assert len(state2.completed_actions) == 0
        assert state2.action_points == 2
        assert state2.round == 1
        assert state2.transport_profile == "needs-coordination"


class TestDataIntegrityAndProvenance:

    def test_locations_geojson_validity(self):
        locations = load_locations()
        assert locations["type"] == "FeatureCollection"
        assert len(locations["features"]) == 3
        feature_ids = {f["id"] for f in locations["features"]}
        assert feature_ids == {"ruskin-high", "rwl-center", "mcc-penn-valley-hsi"}

        for f in locations["features"]:
            geom = f["geometry"]
            assert geom["type"] == "Point"
            coords = geom["coordinates"]
            # Kansas City bounding box roughly: lon [-94.7, -94.4], lat [38.8, 39.2]
            assert -94.70 <= coords[0] <= -94.40
            assert 38.80 <= coords[1] <= 39.20
            props = f["properties"]
            assert props["provenance_type"] == "verified_fact"
            assert props["source_id"] is not None

    def test_programs_json_validity(self):
        programs_data = load_programs()
        programs = programs_data["programs"]
        assert len(programs) >= 3
        p_ids = {p["id"] for p in programs}
        assert "health-start" in p_ids
        assert "early-college-academy" in p_ids
        assert "mcc-healthcare-pathway" in p_ids

        for p in programs:
            assert p["provenance_type"] == "verified_fact"
            assert "verified_source_url" in p
            assert p["verified_source_url"].startswith("http")
            assert "unknowns" in p
            assert isinstance(p["unknowns"], list)

    def test_sources_registry(self):
        sources_data = load_sources()
        sources = sources_data["sources"]
        assert len(sources) >= 5
        for s in sources:
            assert s["category"] in ("verified_fact", "simulation_assumption", "unknown")
            assert s["checked_date"] == "2026-10-12"
            assert s["url"].startswith("http")
