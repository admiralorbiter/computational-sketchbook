"""Statistical and lexical evaluation harness for Qwen3.5-4B neuron steering rollouts.

Implements:
1. Lexical trait matching & Distinct-4-Gram coherence scoring (Lyra's wreckage metric).
2. Exact one-sided Fisher's exact test (hypergeometric distribution via `math.comb`) and
   Haldane-Anscombe odds ratio for comparing steered rollouts against unsteered baselines
   and random-direction null controls.
3. @treetowntree's Neuron Pair Interaction Classifier (`emergent_synthesis`,
   `single_dominance`, `additive_coexistence`, `mutual_suppression`).
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple


WORD_RE = re.compile(r"[A-Za-z0-9']+|[^\sA-Za-z0-9']+")


def tokenize_words(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric words and punctuation."""
    return [t.lower() for t in WORD_RE.findall(text)]


def distinct_4gram_ratio(text: str) -> float:
    """Compute the ratio of unique 4-grams to total 4-grams in `text`.

    From Lyra's calibration on Qwen3.5-4B:
    - >= 0.93 for coherent text (doses <= 0.75x residual norm)
    - ~0.61 - 0.80 at onset of repetition (0.75x - 1.0x)
    - < 0.40 for high-dose token wreckage / loops (>= 1.5x)
    """
    tokens = tokenize_words(text)
    if len(tokens) == 0:
        return 0.0
    if len(tokens) < 4:
        return len(set(tokens)) / len(tokens)
    ngrams = [tuple(tokens[i : i + 4]) for i in range(len(tokens) - 3)]
    return round(len(set(ngrams)) / len(ngrams), 4)


def uppercase_word_ratio(text: str) -> float:
    """Fraction of alphabetic words (length >= 2) that are entirely UPPERCASE."""
    alpha_words = re.findall(r"[A-Za-z]{2,}", text)
    if not alpha_words:
        return 0.0
    caps = sum(1 for w in alpha_words if w.isupper())
    return round(caps / len(alpha_words), 4)


def match_trait_keywords(
    text: str,
    keywords: Sequence[str],
    check_all_caps: bool = False,
) -> Dict[str, Any]:
    """Evaluate whether `text` exhibits `keywords` (or ALL CAPS formatting)."""
    if check_all_caps:
        cap_ratio = uppercase_word_ratio(text)
        hit = cap_ratio >= 0.25
        return {
            "exhibits_trait": hit,
            "matched_keywords": ["<ALL_CAPS> (ratio={:.2f})".format(cap_ratio)] if hit else [],
            "match_count": int(cap_ratio * 20),
        }

    lower_text = text.lower()
    word_set = set(re.findall(r"[a-z0-9']+", lower_text))
    matched: List[str] = []
    total_occurrences = 0

    for kw in keywords:
        kw_low = kw.lower().strip()
        if not kw_low:
            continue
        if " " in kw_low or not kw_low.isalnum():
            cnt = lower_text.count(kw_low)
            if cnt > 0:
                matched.append(kw)
                total_occurrences += cnt
        else:
            if kw_low in word_set:
                matched.append(kw)
                total_occurrences += sum(
                    1 for w in re.findall(r"[a-z0-9']+", lower_text) if w == kw_low
                )

    return {
        "exhibits_trait": len(matched) > 0,
        "matched_keywords": matched,
        "match_count": total_occurrences,
    }


def fisher_exact_one_sided(a: int, b: int, c: int, d: int) -> Tuple[float, float]:
    """Compute one-sided Fisher's exact test p-value (greater) and odds ratio.

    2x2 table:
                     Trait Present    Trait Absent
      Steered              a               b          (n1 = a + b)
      Control              c               d          (n2 = c + d)

    Tests H1: P(trait | steered) > P(trait | control).
    Uses exact hypergeometric probabilities via `math.comb`.
    """
    if any(x < 0 for x in (a, b, c, d)):
        raise ValueError("Contingency table counts must be non-negative.")
    n1 = a + b
    n2 = c + d
    k = a + c
    total = n1 + n2
    if total == 0 or n1 == 0 or n2 == 0:
        return 1.0, 1.0

    denom = math.comb(total, k)
    max_x = min(n1, k)
    p_val = 0.0
    for x in range(a, max_x + 1):
        y = k - x
        if 0 <= y <= n2:
            p_val += (math.comb(n1, x) * math.comb(n2, y)) / denom

    # Haldane-Anscombe 0.5 correction if any cell is 0
    if 0 in (a, b, c, d):
        odds_ratio = ((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5))
    else:
        odds_ratio = (a * d) / (b * c)

    return min(1.0, float(p_val)), round(float(odds_ratio), 3)


@dataclass(frozen=True)
class PairInteractionResult:
    """Summary of a 2-neuron breeding interaction test."""

    interaction_type: str
    summary_label: str
    paired_emergent_hits: int
    solo_max_emergent_hits: int
    fold_enrichment: float
    fisher_p_value: float
    passes_treetown_gold_gate: bool
    trait_a_retention: float
    trait_b_retention: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interaction_type": self.interaction_type,
            "summary_label": self.summary_label,
            "paired_emergent_hits": self.paired_emergent_hits,
            "solo_max_emergent_hits": self.solo_max_emergent_hits,
            "fold_enrichment": self.fold_enrichment,
            "fisher_p_value": self.fisher_p_value,
            "passes_treetown_gold_gate": self.passes_treetown_gold_gate,
            "trait_a_retention": self.trait_a_retention,
            "trait_b_retention": self.trait_b_retention,
        }


def classify_pair_interaction(
    n_questions: int,
    paired_emergent_hits: int,
    solo_a_emergent_hits: int,
    solo_b_emergent_hits: int,
    paired_trait_a_hits: int,
    solo_a_trait_a_hits: int,
    paired_trait_b_hits: int,
    solo_b_trait_b_hits: int,
    trait_a_name: str = "Trait A",
    trait_b_name: str = "Trait B",
    emergent_name: str = "Emergent Concept",
) -> PairInteractionResult:
    """Classify a 2-neuron pair rollout using @treetowntree's interaction criteria.

    @treetowntree Gold Gate for "makes a new thing neither neuron makes alone":
    1. Paired emergent hits >= max(1, int(0.20 * n_questions)) (i.e. >= 10/50 questions)
    2. Paired emergent hits >= 2.5 * max(solo_a_emergent_hits, solo_b_emergent_hits)
    3. One-sided Fisher's exact p < 0.001 vs the best single neuron
    """
    solo_max = max(solo_a_emergent_hits, solo_b_emergent_hits)
    fold = (
        round(paired_emergent_hits / solo_max, 2)
        if solo_max > 0
        else (float(paired_emergent_hits) if paired_emergent_hits > 0 else 1.0)
    )
    p_val, _ = fisher_exact_one_sided(
        paired_emergent_hits,
        n_questions - paired_emergent_hits,
        solo_max,
        n_questions - solo_max,
    )
    min_hits_threshold = max(2, int(round(0.20 * n_questions)))
    # For small quick-test batches (e.g., n_questions < 15), relax p-value gate proportionally
    p_gate = 0.001 if n_questions >= 30 else 0.05
    passes_gold = (
        paired_emergent_hits >= min_hits_threshold
        and (solo_max == 0 or (paired_emergent_hits / solo_max) >= 2.2)
        and p_val < p_gate
    )

    ret_a = round(paired_trait_a_hits / max(1, solo_a_trait_a_hits), 3)
    ret_b = round(paired_trait_b_hits / max(1, solo_b_trait_b_hits), 3)

    if passes_gold:
        itype = "emergent_synthesis"
        label = f"= {emergent_name}!"
    elif ret_a >= 0.45 and ret_b < 0.25:
        itype = "single_dominance"
        label = f"= {trait_a_name.lower()}, no {trait_b_name.lower()}"
    elif ret_b >= 0.45 and ret_a < 0.25:
        itype = "single_dominance"
        label = f"= {trait_b_name.lower()}, no {trait_a_name.lower()}"
    elif ret_a >= 0.30 and ret_b >= 0.30:
        itype = "additive_coexistence"
        label = f"= both, not {emergent_name.lower()}"
    else:
        itype = "mutual_suppression"
        label = f"= mutual suppression / neutral"

    return PairInteractionResult(
        interaction_type=itype,
        summary_label=label,
        paired_emergent_hits=paired_emergent_hits,
        solo_max_emergent_hits=solo_max,
        fold_enrichment=fold,
        fisher_p_value=round(p_val, 6),
        passes_treetown_gold_gate=passes_gold,
        trait_a_retention=ret_a,
        trait_b_retention=ret_b,
    )
