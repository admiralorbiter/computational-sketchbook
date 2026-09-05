"""Evaluation and scoring of partial-information constraints against sealed ground truth."""

import math
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PartialConstraint(BaseModel):
    constraint_type: str  # "bit_block", "interval", "congruence", "approximation"
    target: str = "p"  # "p" or "q"
    params: Dict[str, Any]
    confidence: float = 1.0


class PartialScoringResult(BaseModel):
    total_constraints: int
    valid_constraints: int
    false_constraints: int
    accuracy: float
    information_gain_bits: float
    details: List[Dict[str, Any]] = Field(default_factory=list)


def evaluate_partial_constraints(
    constraints: List[PartialConstraint],
    p_true: int,
    q_true: int,
) -> PartialScoringResult:
    """Score a set of partial constraints against sealed factors p and q.

    Never pass candidate generator code into this evaluation function.
    """
    total = len(constraints)
    if total == 0:
        return PartialScoringResult(
            total_constraints=0,
            valid_constraints=0,
            false_constraints=0,
            accuracy=0.0,
            information_gain_bits=0.0,
        )

    valid_count = 0
    false_count = 0
    details: List[Dict[str, Any]] = []
    total_gain_bits = 0.0

    targets = {"p": p_true, "q": q_true}

    for c in constraints:
        val = targets.get(c.target, p_true)
        c_type = c.constraint_type
        params = c.params
        is_valid = False
        gain = 0.0

        if c_type == "bit_block":
            # e.g. start, end, expected_value
            start = int(params["start"])
            end = int(params["end"])
            expected = int(params["value"])
            mask = ((1 << (end - start)) - 1)
            actual = (val >> start) & mask
            if actual == expected:
                is_valid = True
                gain = float(end - start)
            else:
                is_valid = False

        elif c_type == "interval":
            lower = int(params["lower"])
            upper = int(params["upper"])
            if lower <= val < upper:
                is_valid = True
                # Log2 candidate reduction
                orig_span = 1 << val.bit_length()
                new_span = max(1, upper - lower)
                gain = max(0.0, math.log2(orig_span / new_span))
            else:
                is_valid = False

        elif c_type == "congruence":
            modulus = int(params["modulus"])
            residue = int(params["residue"])
            if (val % modulus) == residue:
                is_valid = True
                gain = max(0.0, math.log2(modulus))
            else:
                is_valid = False

        elif c_type == "approximation":
            p_hat = int(params["p_hat"])
            bound = int(params["bound"])
            if abs(val - p_hat) <= bound:
                is_valid = True
                orig_span = 1 << val.bit_length()
                new_span = max(1, 2 * bound)
                gain = max(0.0, math.log2(orig_span / new_span))
            else:
                is_valid = False

        else:
            is_valid = False

        if is_valid:
            valid_count += 1
            total_gain_bits += gain
        else:
            false_count += 1

        details.append({
            "constraint_type": c_type,
            "target": c.target,
            "valid": is_valid,
            "gain_bits": gain if is_valid else 0.0,
        })

    accuracy = valid_count / total if total > 0 else 0.0

    return PartialScoringResult(
        total_constraints=total,
        valid_constraints=valid_count,
        false_constraints=false_count,
        accuracy=accuracy,
        information_gain_bits=total_gain_bits,
        details=details,
    )
