"""Relation database, linear dependency solver over F2, and exact factor extraction."""

import math
from typing import Any, Dict, List, Optional, Tuple
import gmpy2
from nsb.verifier.factor import FactorVerificationResult, verify_factors


def solve_f2_dependencies(matrix_rows: List[List[int]]) -> List[List[int]]:
    """Gaussian elimination over F2 to find non-zero null space vectors."""
    n_rows = len(matrix_rows)
    if n_rows == 0:
        return []
    n_cols = len(matrix_rows[0])

    augmented = [
        [matrix_rows[i][j] % 2 for j in range(n_cols)] + [1 if i == k else 0 for k in range(n_rows)]
        for i in range(n_rows)
    ]

    pivot_row = 0
    for col in range(n_cols):
        if pivot_row >= n_rows:
            break

        found = -1
        for r in range(pivot_row, n_rows):
            if augmented[r][col] == 1:
                found = r
                break

        if found != -1:
            augmented[pivot_row], augmented[found] = augmented[found], augmented[pivot_row]
            for r in range(n_rows):
                if r != pivot_row and augmented[r][col] == 1:
                    augmented[r] = [
                        (a ^ b) for a, b in zip(augmented[r], augmented[pivot_row])
                    ]
            pivot_row += 1

    null_combinations: List[List[int]] = []
    for r in range(n_rows):
        if all(augmented[r][c] == 0 for c in range(n_cols)):
            combo = [idx for idx in range(n_rows) if augmented[r][n_cols + idx] == 1]
            if combo:
                null_combinations.append(combo)

    return null_combinations


def extract_factors_from_relations(
    relations: List[Dict[str, Any]],
    N: int,
    factor_base: List[int],
) -> Tuple[bool, Optional[List[int]], Optional[FactorVerificationResult]]:
    """Extract factors of N from a collection of smooth relations (CVP or square)."""
    n_fb = len(factor_base)
    if len(relations) < n_fb + 1:
        return False, None, None

    # Check relation format: Schnorr CVP vs square neighborhood
    is_schnorr_cvp = "u" in relations[0] and "row_mod2" in relations[0]

    if is_schnorr_cvp:
        matrix_rows = [rel["row_mod2"] for rel in relations]
        dependencies = solve_f2_dependencies(matrix_rows)

        for combo in dependencies:
            tot_sign = 0
            tot_exp = [0] * n_fb
            X = 1
            for idx in combo:
                X = (X * relations[idx]["u"]) % N
                tot_sign ^= relations[idx]["sign"]
                for i in range(n_fb):
                    tot_exp[i] += relations[idx]["combined_exp"][i]

            # Sign must be even
            if tot_sign != 0 or any(c % 2 != 0 for c in tot_exp):
                continue

            Y = 1
            for i, p in enumerate(factor_base):
                Y = (Y * pow(p, tot_exp[i] // 2, N)) % N

            for cand in [abs(X - Y), (X + Y) % N]:
                if cand == 0:
                    continue
                g = math.gcd(cand, N)
                if 1 < g < N:
                    p_val = g
                    q_val = N // g
                    norm = [p_val, q_val] if p_val <= q_val else [q_val, p_val]
                    verif = verify_factors(N, norm[0], norm[1])
                    if verif.verified:
                        return True, norm, verif

    else:
        matrix_rows = [[e % 2 for e in rel["exponents"]] for rel in relations]
        dependencies = solve_f2_dependencies(matrix_rows)

        for combo in dependencies:
            X = 1
            total_exp = [0] * n_fb

            for idx in combo:
                X = (X * relations[idx]["x"]) % N
                for j, exp in enumerate(relations[idx]["exponents"]):
                    total_exp[j] += exp

            Y = 1
            for p, exp in zip(factor_base, total_exp):
                if exp % 2 != 0:
                    continue
                Y = (Y * pow(p, exp // 2, N)) % N

            # Test gcd(X - Y, N) and gcd(X + Y, N)
            for cand_diff in [abs(X - Y), (X + Y) % N]:
                if cand_diff == 0:
                    continue
                g = math.gcd(cand_diff, N)
                if 1 < g < N:
                    p_val = g
                    q_val = N // g
                    norm = [p_val, q_val] if p_val <= q_val else [q_val, p_val]
                    verif = verify_factors(N, norm[0], norm[1])
                    if verif.verified:
                        return True, norm, verif

    return False, None, None

