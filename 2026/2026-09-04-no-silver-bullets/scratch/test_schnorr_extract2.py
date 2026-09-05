import math
from fractions import Fraction
from nsb.tracks.tensor_lattice.lattice import get_factor_base
from nsb.tracks.partial_information.lattice_root import lll_reduction
from nsb.tracks.tensor_lattice.sampler import check_smooth_and_factor
from nsb.tracks.tensor_lattice.relation import solve_f2_dependencies

p_true = 641
q_true = 1061
N = p_true * q_true

fb_size = 15
factor_base = get_factor_base(fb_size)
scale_c = 4
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

relations = []
for k_mult in range(1, 150):
    target = [Fraction(0)] * (n + 1)
    target[n] = Fraction(int(round((10**scale_c) * math.log(k_mult * N))))

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
    u_exp = [0] * n
    for idx, (p, exp) in enumerate(zip(factor_base, e)):
        if exp > 0:
            u *= (p**exp)
            u_exp[idx] = exp
        elif exp < 0:
            v *= (p**(-exp))

    diff = abs(u - v * k_mult * N)
    if diff > 1 and diff % N != 0:
        exp_diff = check_smooth_and_factor(diff, factor_base)
        if exp_diff is not None:
            # Combined exponent of (u * diff)
            combined_exp = [u_exp[i] + exp_diff[i] for i in range(n)]
            relations.append({
                "u": u,
                "diff": diff,
                "combined_exp": combined_exp,
                "rel_mod2": [c % 2 for c in combined_exp],
            })

print(f"Collected {len(relations)} relations.")
if len(relations) >= n:
    M = [r["rel_mod2"] for r in relations]
    deps = solve_f2_dependencies(M)
    print(f"Found {len(deps)} dependencies.")
    for dep in deps:
        X = 1
        tot_exp = [0] * n
        for idx in dep:
            X = (X * relations[idx]["u"]) % N
            for i in range(n):
                tot_exp[i] += relations[idx]["combined_exp"][i]

        Y = 1
        for i, p in enumerate(factor_base):
            assert tot_exp[i] % 2 == 0
            Y = (Y * pow(p, tot_exp[i] // 2, N)) % N

        g1 = math.gcd(abs(X - Y), N)
        g2 = math.gcd((X + Y) % N, N)
        print(f"dep: X={X}, Y={Y}, gcd1={g1}, gcd2={g2}")
        if 1 < g1 < N:
            print("SUCCESS! Non-trivial factor found:", g1, N // g1)
            break
        if 1 < g2 < N:
            print("SUCCESS! Non-trivial factor found:", g2, N // g2)
            break
