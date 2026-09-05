import math
from fractions import Fraction
from nsb.tracks.tensor_lattice.lattice import get_factor_base
from nsb.tracks.partial_information.lattice_root import lll_reduction
from nsb.tracks.tensor_lattice.sampler import check_smooth_and_factor

# Let's test on N = 143 (11 * 13) and N = 680101 (641 * 1061)
for N in [143, 680101]:
    fb = get_factor_base(12)
    n = len(fb)
    scale_c = 3
    basis = []
    for i, p in enumerate(fb):
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

    # Babai
    curr = [Fraction(x) for x in target]
    coeffs = [0] * n
    for i in reversed(range(n)):
        proj = dot(curr, b_star[i]) / dot(b_star[i], b_star[i])
        k = int(round(proj))
        coeffs[i] = k
        for col in range(n + 1):
            curr[col] -= k * red[i][col]

    lat_point = [Fraction(0)] * (n + 1)
    for i in range(n):
        for col in range(n + 1):
            lat_point[col] += coeffs[i] * red[i][col]

    e = [int(lat_point[i]) for i in range(n)]
    u = 1; v = 1
    for p, exp in zip(fb, e):
        if exp > 0: u *= (p**exp)
        elif exp < 0: v *= (p**(-exp))
    diff = abs(u - v * N)
    print(f"N={N}: u={u}, v={v}, diff={diff}, smooth={check_smooth_and_factor(diff, fb) is not None}")
