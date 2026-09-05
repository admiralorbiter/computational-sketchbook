import math
from fractions import Fraction
from typing import List, Tuple
import gmpy2
from nsb.tracks.tensor_lattice.lattice import get_factor_base

def build_schnorr_target_lattice(factor_base: List[int], scale_c: int = 3):
    """
    Constructs n-rank lattice in (n+1) dimensions:
    For prime p_j (j = 1..n):
    row j has:
      col j: weight w_j (e.g. 1)
      col n: round(10^scale_c * ln(p_j))
      other cols: 0
    """
    n = len(factor_base)
    basis = []
    for i, p in enumerate(factor_base):
        row = [Fraction(0)] * (n + 1)
        row[i] = Fraction(1)
        row[n] = Fraction(int(round((10**scale_c) * math.log(p))))
        basis.append(row)
    return basis

def make_target(N: int, n: int, scale_c: int = 3):
    target = [Fraction(0)] * (n + 1)
    target[n] = Fraction(int(round((10**scale_c) * math.log(N))))
    return target

print("Target lattice builder defined.")
