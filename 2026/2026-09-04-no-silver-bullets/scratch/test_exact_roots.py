import math

def eval_poly_exact(coeffs, x):
    """Evaluate sum_{i=0}^d coeffs[i] * x^i using Horner's method with exact integers."""
    val = 0
    for c in reversed(coeffs):
        val = val * x + c
    return val

def poly_derivative(coeffs):
    """Exact derivative of polynomial."""
    return [i * coeffs[i] for i in range(1, len(coeffs))]

def find_integer_roots_exact(coeffs, X):
    """Find all integer roots r in [-X, X] such that P(r) == 0 using exact arithmetic."""
    # Trim leading zero coefficients
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs = coeffs[:-1]

    if len(coeffs) <= 1:
        return []

    # If c0 == 0, x = 0 is a root
    roots = []
    if coeffs[0] == 0:
        roots.append(0)
        # divide out x
        while len(coeffs) > 1 and coeffs[0] == 0:
            coeffs = coeffs[1:]
        if len(coeffs) <= 1:
            return roots

    # Degree 1: c1 * x + c0 = 0 => x = -c0 / c1
    if len(coeffs) == 2:
        c0, c1 = coeffs[0], coeffs[1]
        if (-c0) % c1 == 0:
            r = (-c0) // c1
            if abs(r) <= X:
                roots.append(r)
        return roots

    # Degree 2: c2 * x^2 + c1 * x + c0 = 0
    if len(coeffs) == 3:
        c0, c1, c2 = coeffs[0], coeffs[1], coeffs[2]
        disc = c1 * c1 - 4 * c2 * c0
        if disc >= 0:
            sq = math.isqrt(disc)
            if sq * sq == disc:
                for num in [-c1 + sq, -c1 - sq]:
                    den = 2 * c2
                    if num % den == 0:
                        r = num // den
                        if abs(r) <= X and r not in roots:
                            roots.append(r)
        return roots

    # For degree >= 3:
    # Use exact recursive root isolation via derivative critical points:
    # 1. Find roots of derivative P'(x) in [-X, X] to find all monotonicity intervals
    deriv = poly_derivative(coeffs)
    crit_pts = sorted([-X] + find_integer_roots_exact(deriv, X) + [X])

    # In each interval [a, b], P(x) is monotonic (or approximately monotonic between int critical points)
    # Refine integer roots in each sub-interval using binary search / bisection
    for idx in range(len(crit_pts) - 1):
        left = crit_pts[idx]
        right = crit_pts[idx + 1]

        f_left = eval_poly_exact(coeffs, left)
        f_right = eval_poly_exact(coeffs, right)

        if f_left == 0 and left not in roots:
            roots.append(left)
        if f_right == 0 and right not in roots:
            roots.append(right)

        # Check for sign change in interval
        if (f_left > 0 and f_right < 0) or (f_left < 0 and f_right > 0):
            # Monotonic binary search for exact integer root
            lo, hi = left, right
            while lo <= hi:
                mid = (lo + hi) // 2
                f_mid = eval_poly_exact(coeffs, mid)
                if f_mid == 0:
                    if abs(mid) <= X and mid not in roots:
                        roots.append(mid)
                    break
                # Check sign
                if (f_left > 0 and f_mid > 0) or (f_left < 0 and f_mid < 0):
                    lo = mid + 1
                else:
                    hi = mid - 1

    return roots

# Test with our cubic polynomial from earlier:
# Diff polynomial coeffs: [338171182448640, 1441440414668, -538132015, -43, 0]
coeffs = [338171182448640, 1441440414668, -538132015, -43]
X = 4096
r = find_integer_roots_exact(coeffs, X)
print(f"Exact integer roots in [-{X}, {X}]:", r)
