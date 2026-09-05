from fractions import Fraction

def poly_deg(poly):
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return len(poly) - 1

def poly_div_rem(p1, p2):
    # p1, p2 are lists of Fraction, index = power of x
    deg1 = poly_deg(p1)
    deg2 = poly_deg(p2)
    if deg2 < 0 or (deg2 == 0 and p2[0] == 0):
        raise ZeroDivisionError()
    if deg1 < deg2:
        return [Fraction(0)], [Fraction(x) for x in p1]
    
    rem = [Fraction(x) for x in p1]
    quot = [Fraction(0)] * (deg1 - deg2 + 1)
    
    for i in range(deg1 - deg2, -1, -1):
        d_rem = poly_deg(rem)
        if d_rem == deg2 + i:
            coeff = rem[d_rem] / p2[deg2]
            quot[i] = coeff
            for j in range(deg2 + 1):
                rem[i + j] -= coeff * p2[j]
    return quot, rem

def build_sturm_chain(coeffs):
    # coeffs are Fraction or int
    p0 = [Fraction(x) for x in coeffs]
    while len(p0) > 1 and p0[-1] == 0:
        p0.pop()
    if len(p0) <= 1:
        return []
    
    # p1 = derivative of p0
    p1 = [p0[i] * i for i in range(1, len(p0))]
    chain = [p0, p1]
    
    while True:
        p_prev2 = chain[-2]
        p_prev1 = chain[-1]
        if poly_deg(p_prev1) <= 0:
            break
        _, rem = poly_div_rem(p_prev2, p_prev1)
        if poly_deg(rem) < 0 or all(x == 0 for x in rem):
            break
        # Negate remainder
        neg_rem = [-x for x in rem]
        while len(neg_rem) > 1 and neg_rem[-1] == 0:
            neg_rem.pop()
        chain.append(neg_rem)
    return chain

def eval_poly_frac(p, x):
    val = Fraction(0)
    for c in reversed(p):
        val = val * x + c
    return val

def sturm_sign_changes(chain, x):
    signs = []
    for p in chain:
        val = eval_poly_frac(p, x)
        if val > 0:
            signs.append(1)
        elif val < 0:
            signs.append(-1)
    # Count sign changes
    changes = 0
    for i in range(len(signs) - 1):
        if signs[i] * signs[i + 1] < 0:
            changes += 1
    return changes

def isolate_integer_roots_sturm(coeffs, X):
    chain = build_sturm_chain(coeffs)
    if not chain:
        return []
    
    # Bisect intervals in [-X, X]
    intervals = [(-X, X)]
    isolated_intervals = []
    
    while intervals:
        a, b = intervals.pop()
        va = sturm_sign_changes(chain, Fraction(a))
        vb = sturm_sign_changes(chain, Fraction(b))
        roots_in_interval = va - vb
        if roots_in_interval == 0:
            continue
        if b - a <= 1:
            isolated_intervals.append((a, b))
        else:
            mid = (a + b) // 2
            intervals.append((a, mid))
            intervals.append((mid, b))
            
    # For each isolated interval [a, b], test integer endpoints a and b
    integer_roots = set()
    p0 = [Fraction(x) for x in coeffs]
    for a, b in isolated_intervals:
        for cand in [a, b]:
            if abs(cand) <= X and eval_poly_frac(p0, Fraction(cand)) == 0:
                integer_roots.add(cand)
                
    return sorted(list(integer_roots))

# Test on our exact cubic polynomial:
coeffs = [338171182448640, 1441440414668, -538132015, -43]
X = 4096
roots = isolate_integer_roots_sturm(coeffs, X)
print(f"Sturm exact integer roots in [-{X}, {X}]:", roots)
