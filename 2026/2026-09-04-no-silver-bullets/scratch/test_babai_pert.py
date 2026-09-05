import math
from fractions import Fraction
from typing import List, Tuple
import gmpy2
from nsb.tracks.tensor_lattice.lattice import get_factor_base
from nsb.tracks.partial_information.lattice_root import lll_reduction
from nsb.tracks.tensor_lattice.sampler import check_smooth_and_factor

p_true = 641
q_true = 1061
N = p_true * q_true

fb_size = 15
factor_base = get_factor_base(fb_size)
scale_c = 3
n = len(factor_base)

basis = []
for i, p in enumerate(factor_base):
    row = [Fraction(0)] * (n + 1)
    row[i] = Fraction(1)
    row[n] = Fraction(int(round((10**scale_c) * math.log(p))))
    basis.append(row)

red = lll_reduction(basis)

def dot(u, v):
    return sum(a * b for a, b in zip(u, v))

b_star = []
for i in range(n):
    v = [Fraction(x) for x in red[i]]
    for j in range(i):
        mu = dot(red[i], b_star[j]) / dot(b_star[j], b_star[j])
        v = [v[k] - mu * b_star[j][k] for k in range(n + 1)]
    b_star.append(v)

target = [Fraction(0)] * (n + 1)
target[n] = Fraction(int(round((10**scale_c) * math.log(N))))

# Sample perturbations around Babai
import itertools

smooth_relations = []
for offsets in itertools.product([-1, 0, 1], repeat=min(n, 6)):
    pert = list(offsets) + [0] * (n - len(offsets))
    curr = [Fraction(x) for x in target]
    coeffs = [0] * n
    for i in reversed(range(n)):
        proj = dot(curr, b_star[i]) / dot(b_star[i], b_star[i])
        k = int(round(proj)) + pert[i]
        coeffs[i] = k
        for col in range(n + 1):
            curr[col] -= k * red[i][col]

    lat_point = [Fraction(0)] * (n + 1)
    for i in range(n):
        for col in range(n + 1):
            lat_point[col] += coeffs[i] * red[i][col]

    e = [int(lat_point[i]) for i in range(n)]
    u = 1
    v = 1
    for prime, exp in zip(factor_base, e):
        if exp > 0:
            u *= (prime ** exp)
        elif exp < 0:
            v *= (prime ** (-exp))

    diff = abs(u - v * N)
    if diff > 1 and diff % N != 0:
        exp_diff = check_smooth_and_factor(diff, factor_base)
        if exp_diff is not None:
            smooth_relations.append((u, v, diff, e, exp_diff))
            print(f"FOUND SMOOTH RELATION! u={u}, v={v}, diff={diff}")
            if len(smooth_relations) >= 5:
                break

print(f"Total smooth relations found: {len(smooth_relations)}")
