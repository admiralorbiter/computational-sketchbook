"""Exact integer factor verification and primality testing."""

from typing import List, Optional, Tuple, Union
import gmpy2
from pydantic import BaseModel


class FactorVerificationResult(BaseModel):
    verified: bool
    status: str  # "SUCCESS", "FAILED", "TRIVIAL", "INVALID_PRODUCT", "COMPOSITE_FACTOR"
    factors: Optional[List[str]] = None
    error_message: Optional[str] = None


def verify_factors(
    N: Union[int, str],
    p_cand: Union[int, str],
    q_cand: Optional[Union[int, str]] = None,
    require_prime: bool = True,
) -> FactorVerificationResult:
    """Deterministically verify factor candidate(s) against public modulus N.

    Args:
        N: The target semiprime.
        p_cand: First factor candidate.
        q_cand: Optional second factor candidate. If None, derived as N // p_cand.
        require_prime: Whether factors must be prime.

    Returns:
        FactorVerificationResult with verification status and details.
    """
    try:
        n_val = int(N)
        p_val = int(p_cand)
    except (ValueError, TypeError) as e:
        return FactorVerificationResult(
            verified=False,
            status="FAILED",
            error_message=f"Non-integer factor input: {e}",
        )

    if n_val <= 3:
        return FactorVerificationResult(
            verified=False,
            status="FAILED",
            error_message="Modulus N must be > 3",
        )

    # Check non-triviality
    if p_val <= 1 or p_val >= n_val:
        return FactorVerificationResult(
            verified=False,
            status="TRIVIAL",
            error_message=f"Factor p={p_val} is trivial for N={n_val}",
        )

    if q_cand is None:
        if n_val % p_val != 0:
            return FactorVerificationResult(
                verified=False,
                status="INVALID_PRODUCT",
                error_message=f"Candidate p={p_val} does not divide N={n_val}",
            )
        q_val = n_val // p_val
    else:
        try:
            q_val = int(q_cand)
        except (ValueError, TypeError) as e:
            return FactorVerificationResult(
                verified=False,
                status="FAILED",
                error_message=f"Non-integer factor q input: {e}",
            )

    # Verify exact product
    if p_val * q_val != n_val:
        return FactorVerificationResult(
            verified=False,
            status="INVALID_PRODUCT",
            error_message=f"Product p*q ({p_val * q_val}) != N ({n_val})",
        )

    # Check non-triviality of q
    if q_val <= 1 or q_val >= n_val:
        return FactorVerificationResult(
            verified=False,
            status="TRIVIAL",
            error_message=f"Factor q={q_val} is trivial for N={n_val}",
        )

    # Normalize order
    if p_val > q_val:
        p_val, q_val = q_val, p_val

    # Check primality if required
    if require_prime:
        if not gmpy2.is_prime(p_val, 25):
            return FactorVerificationResult(
                verified=False,
                status="COMPOSITE_FACTOR",
                factors=[str(p_val), str(q_val)],
                error_message=f"Factor p={p_val} is composite",
            )
        if not gmpy2.is_prime(q_val, 25):
            return FactorVerificationResult(
                verified=False,
                status="COMPOSITE_FACTOR",
                factors=[str(p_val), str(q_val)],
                error_message=f"Factor q={q_val} is composite",
            )

    return FactorVerificationResult(
        verified=True,
        status="SUCCESS",
        factors=[str(p_val), str(q_val)],
        error_message=None,
    )
