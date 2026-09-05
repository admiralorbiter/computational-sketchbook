"""Multi-fraction calibration ladder for Track C (Partial Information Bridge).

Maps empirical small-root recovery success rates and timings across known MSB fractions:
25%, 35%, 40%, 45%, 50%, 55%, 60% without synthetic placeholders.
"""

from dataclasses import asdict, dataclass
import time
from typing import Any, Dict, List, Optional
from nsb.tracks.partial_information.bridge import PartialInformationBridge


@dataclass
class CalibrationPointResult:
    bits: int
    fraction: float
    known_bits: int
    total_factor_bits: int
    shift: int
    success: bool
    wall_seconds: float
    cpu_seconds: float
    is_synthetic: bool = False
    method: str = "sturm_lll"


def generate_oracle_slices(p: int, fractions: Optional[List[float]] = None) -> List[Dict[str, Any]]:
    """Generate genuine MSB oracle slices for factor p across a ladder of fractions."""
    fractions = fractions or [0.25, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
    p_bits = p.bit_length()
    slices: List[Dict[str, Any]] = []

    for frac in sorted(fractions):
        known_msb = max(1, int(round(p_bits * frac)))
        shift = p_bits - known_msb
        msb_val = p >> shift
        slices.append({
            "target": "p",
            "fraction": frac,
            "factor_bit_length": p_bits,
            "known_bits": known_msb,
            "shift": shift,
            "msb_value": msb_val,
        })

    return slices


def run_calibration_ladder(
    N: int,
    bits: int,
    oracle_slices: List[Dict[str, Any]],
    bridge: Optional[PartialInformationBridge] = None,
    max_seconds_per_point: float = 5.0,
) -> List[CalibrationPointResult]:
    """Execute calibration ladder across genuine MSB slices."""
    bridge = bridge or PartialInformationBridge()
    results: List[CalibrationPointResult] = []

    for sl in oracle_slices:
        frac = sl["fraction"]
        f_bits = sl["factor_bit_length"]
        msb_val = sl["msb_value"]
        shift = sl["shift"]
        known_bits = sl["known_bits"]

        res = bridge.recover_from_oracle_msb(
            N=N,
            msb_value=msb_val,
            shift=shift,
            factor_bit_length=f_bits,
            max_seconds=max_seconds_per_point,
            no_fallback=True,
        )

        results.append(
            CalibrationPointResult(
                bits=bits,
                fraction=frac,
                known_bits=known_bits,
                total_factor_bits=f_bits,
                shift=shift,
                success=res.success,
                wall_seconds=res.wall_seconds,
                cpu_seconds=res.cpu_seconds,
                is_synthetic=False,
                method="sturm_lll",
            )
        )

    return results
