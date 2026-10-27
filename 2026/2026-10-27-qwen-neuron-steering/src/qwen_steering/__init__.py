"""Qwen3.5-4B Mechanistic Neuron Steering & Breeding Laboratory package."""
from .engine import QwenSteeringEngine
from .evaluation import (
    PairInteractionResult,
    classify_pair_interaction,
    distinct_4gram_ratio,
    fisher_exact_one_sided,
    match_trait_keywords,
    uppercase_word_ratio,
)
from .ollama_bridge import OllamaBridge, export_recipe_artifacts, write_gguf_control_vector
from .registry import NeuronPush, NeuronZooRegistry, SteeringRecipe
from .widget import render_steering_lab_widget

__all__ = [
    "QwenSteeringEngine",
    "PairInteractionResult",
    "classify_pair_interaction",
    "distinct_4gram_ratio",
    "fisher_exact_one_sided",
    "match_trait_keywords",
    "uppercase_word_ratio",
    "OllamaBridge",
    "export_recipe_artifacts",
    "write_gguf_control_vector",
    "NeuronPush",
    "NeuronZooRegistry",
    "SteeringRecipe",
    "render_steering_lab_widget",
]
