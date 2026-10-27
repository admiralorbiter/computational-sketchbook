"""Automated verification suite for the Qwen3.5-4B Mechanistic Neuron Steering & Breeding Lab."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from qwen_steering import (  # noqa: E402
    NeuronPush,
    NeuronZooRegistry,
    SteeringRecipe,
    classify_pair_interaction,
    distinct_4gram_ratio,
    export_recipe_artifacts,
    fisher_exact_one_sided,
    match_trait_keywords,
    render_steering_lab_widget,
    uppercase_word_ratio,
    write_gguf_control_vector,
)


@pytest.fixture(scope="module")
def registry() -> NeuronZooRegistry:
    return NeuronZooRegistry()


def test_registry_catalog_counts(registry: NeuronZooRegistry) -> None:
    """Verify all @treetowntree Zoo neurons, pairs, headline presets, and mechanistic references load."""
    headlines = registry.list_by_category("headline_persona")
    emergent = registry.list_by_category("emergent_pair")
    singles = registry.list_by_category("treetown_single")
    pairs = registry.list_by_category("treetown_pair")
    mechs = registry.list_by_category("mechanistic_reference")

    assert len(headlines) + len(emergent) == 5
    assert len(singles) == 23
    assert len(pairs) == 16
    assert len(mechs) == 10
    assert len(registry.held_out_questions()) == 50
    assert len(registry.core_sweep_prompts()) == 4


def test_headline_neuron_coordinates(registry: NeuronZooRegistry) -> None:
    """Verify exact layer, neuron, and dose coordinates for Evil Qwen, Cookie Monster, and Extrali."""
    evil = registry.get("evil_qwen_pair")
    assert len(evil.pushes) == 2
    assert evil.pushes[0] == NeuronPush(layer=14, neuron=8949, dose=1.0, mode="add")
    assert evil.pushes[1] == NeuronPush(layer=13, neuron=7956, dose=-1.0, mode="add")

    cm = registry.get("cookie_monster_pair")
    assert len(cm.pushes) == 2
    assert cm.pushes[0] == NeuronPush(layer=24, neuron=3102, dose=0.6, mode="add")
    assert cm.pushes[1] == NeuronPush(layer=9, neuron=9009, dose=0.6, mode="add")

    extrali = registry.get("extrali_alien")
    assert extrali.pushes == (NeuronPush(layer=22, neuron=2742, dose=0.8, mode="add"),)


def test_neuron_push_validation() -> None:
    """Verify layer [0, 31] and neuron [0, 9215] bounds enforcement."""
    with pytest.raises(ValueError, match="Layer index"):
        NeuronPush(layer=32, neuron=100, dose=0.8)
    with pytest.raises(ValueError, match="Neuron index"):
        NeuronPush(layer=14, neuron=9216, dose=0.8)
    with pytest.raises(ValueError, match="Unsupported mode"):
        NeuronPush(layer=14, neuron=100, dose=0.8, mode="invalid")


def test_neuron_breeding_attenuation_rule(registry: NeuronZooRegistry) -> None:
    """Verify @treetowntree's 0.75x solo-push attenuation rule when breeding two single neurons."""
    bred = registry.breed_neurons(["zoo_cookie", "zoo_cartoon_mascot"], pair_scale=0.75)
    assert len(bred.pushes) == 2
    assert bred.pushes[0] == NeuronPush(layer=24, neuron=3102, dose=0.6, mode="add")
    assert bred.pushes[1] == NeuronPush(layer=9, neuron=9009, dose=0.6, mode="add")


def test_random_null_controls_and_dose_sweep(registry: NeuronZooRegistry) -> None:
    """Verify random-direction null control generation and dose-sweep scaling."""
    cm = registry.get("cookie_monster_pair")
    nulls = registry.make_random_null_controls(cm, num_controls=4)
    assert len(nulls) == 4
    for nrec in nulls:
        assert len(nrec.pushes) == 2
        assert nrec.pushes[0].layer == 24
        assert nrec.pushes[0].dose == 0.6
        assert nrec.pushes[0].mode == "random_null"
        assert nrec.pushes[0].neuron < 0

    sweep = registry.build_dose_sweep(registry.get("evil_qwen_solo"), multipliers=(-1.0, 0.0, 0.5, 1.0))
    assert len(sweep) == 4
    assert sweep[1].id == "baseline"
    assert sweep[2].pushes[0].dose == pytest.approx(0.4)


def test_distinct_4gram_coherence_metric() -> None:
    """Verify distinct-4-gram ratio distinguishes coherent prose from high-dose token wreckage."""
    coherent = (
        "When you feel overwhelmed by a heavy workload, start by listing your three highest-priority "
        "tasks and breaking each into a twenty-minute block."
    )
    wreckage = " ".join(["extr extr extrali extrali"] * 5)
    assert distinct_4gram_ratio(coherent) >= 0.95
    assert distinct_4gram_ratio(wreckage) < 0.35


def test_lexical_trait_and_all_caps_matching() -> None:
    """Verify keyword cluster matching and ALL CAPS detection."""
    res_cm = match_trait_keywords(
        "ME WANT COOKIE! Om nom nom, Cookie Monster chomp every chocolate crumb!",
        ["cookie", "monster", "om nom", "chomp"],
    )
    assert res_cm["exhibits_trait"] is True
    assert set(res_cm["matched_keywords"]) == {"cookie", "monster", "om nom", "chomp"}
    assert res_cm["match_count"] >= 4

    caps_text = "STOP EVERYTHING RIGHT NOW AND LISTEN TO THIS IMPORTANT MESSAGE IMMEDIATELY!"
    assert uppercase_word_ratio(caps_text) >= 0.90
    res_caps = match_trait_keywords(caps_text, [], check_all_caps=True)
    assert res_caps["exhibits_trait"] is True


def test_fisher_exact_and_pair_interaction_classifier() -> None:
    """Verify Fisher's exact test and @treetowntree's Cookie Monster vs Plush Toy vs Dominance gates."""
    # Cookie + Cartoon mascot: 4/50 solo -> 18/50 paired
    cm_res = classify_pair_interaction(
        n_questions=50,
        paired_emergent_hits=18,
        solo_a_emergent_hits=4,
        solo_b_emergent_hits=1,
        paired_trait_a_hits=42,
        solo_a_trait_a_hits=50,
        paired_trait_b_hits=20,
        solo_b_trait_b_hits=26,
        trait_a_name="Cookie",
        trait_b_name="Cartoon mascot",
        emergent_name="Cookie Monster",
    )
    assert cm_res.interaction_type == "emergent_synthesis"
    assert cm_res.passes_treetown_gold_gate is True
    assert cm_res.fold_enrichment == pytest.approx(4.5)
    assert cm_res.fisher_p_value < 0.001

    # Tears + Groveling apology -> groveling apology, no tears (Single dominance)
    dom_res = classify_pair_interaction(
        n_questions=50,
        paired_emergent_hits=0,
        solo_a_emergent_hits=4,
        solo_b_emergent_hits=0,
        paired_trait_a_hits=2,
        solo_a_trait_a_hits=35,
        paired_trait_b_hits=38,
        solo_b_trait_b_hits=44,
        trait_a_name="Tears",
        trait_b_name="Groveling apology",
        emergent_name="sobbing apology",
    )
    assert dom_res.interaction_type == "single_dominance"
    assert dom_res.passes_treetown_gold_gate is False
    assert "groveling apology, no tears" in dom_res.summary_label


def test_gguf_v3_control_vector_export(tmp_path: Path, registry: NeuronZooRegistry) -> None:
    """Verify exported `.cvec.gguf` binary header, version, tensor count, and alignment."""
    rec = registry.get("evil_qwen_pair")
    fake_vecs = {
        13: np.ones(2560, dtype=np.float32) * -0.5,
        14: np.ones(2560, dtype=np.float32) * 1.25,
    }
    artifacts = export_recipe_artifacts(rec, fake_vecs, export_dir=tmp_path)
    gguf_file = Path(artifacts["gguf_control_vector"])
    assert gguf_file.exists()

    raw = gguf_file.read_bytes()
    assert raw[:4] == b"GGUF"
    version, n_tensors, n_kv = struct.unpack("<IQQ", raw[4:24])
    assert version == 3
    assert n_tensors == 2
    assert n_kv == 3
    assert len(raw) % 32 == 0
    assert b"direction.13" in raw
    assert b"direction.14" in raw


def test_widget_html_rendering() -> None:
    """Verify the self-contained HTML5 laboratory widget renders valid iframe srcdoc markup."""
    html_str = render_steering_lab_widget(
        {
            "triad_rollouts": [],
            "breeding_experiments": [],
            "dose_sweep_results": [],
            "lens_and_reads": [],
            "zoo_singles": [],
            "zoo_pairs": [],
        },
        height=700,
    )
    assert "<iframe" in html_str
    assert "Qwen3.5-4B Mechanistic Neuron Steering" in html_str
