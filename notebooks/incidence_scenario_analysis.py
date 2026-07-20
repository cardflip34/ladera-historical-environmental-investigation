#!/usr/bin/env python3
"""LEHRP — Ewing sarcoma incidence scenario analysis.

Executable as a plain script (`python3 incidence_scenario_analysis.py`) or cell-by-cell in
Jupyter. Pure standard library (uses math only). EVERY output is HYPOTHETICAL — based on
UNVERIFIED public case reports and ESTIMATED population. Nothing here confirms a cluster or
establishes causation. See ../METHODOLOGY.md and ../CLAIMS_AND_LIMITATIONS.md.
"""
import math

# ---------------------------------------------------------------------------
# 1. Verified inputs (see research/demographics/). Ladera Ranch CDP.
# ---------------------------------------------------------------------------
CHILD_POP_0_19 = 9115      # ACS 2020-2024 5-yr
CHILD_POP_10_19 = 4906     # peak-age window
YEARS = 14                 # 2013-2026 window
PY_0_19 = CHILD_POP_0_19 * YEARS      # ~127,610 person-years (assumes ~constant child pop)
PY_10_19 = CHILD_POP_10_19 * YEARS    # ~68,684 person-years

# Baseline Ewing sarcoma incidence rates (per million per year), from SEER/CI5 (see
# research/demographics/incidence_rates.csv and research/literature/).
RATE_ALL = 3.0     # ages 0-19, all races (central)
RATE_WHITE = 4.0   # ancestry-adjusted upper for NH-white-majority community
RATE_PEAK = 4.58   # ages 10-19, North America peak-age


# ---------------------------------------------------------------------------
# 2. Exact (Garwood) Poisson 95% confidence limits for the mean given observed count.
# ---------------------------------------------------------------------------
def _chi2_ppf(p, df):
    """Inverse chi-square CDF via Wilson-Hilferty, refined by Newton on the gamma CDF."""
    # Wilson-Hilferty starting point
    x = df * (1 - 2.0 / (9 * df) + _norm_ppf(p) * math.sqrt(2.0 / (9 * df))) ** 3
    if x <= 0:
        x = 1e-6
    for _ in range(60):
        cdf = _gammainc(df / 2.0, x / 2.0)
        pdf = 0.5 * (x / 2.0) ** (df / 2.0 - 1) * math.exp(-x / 2.0) / math.gamma(df / 2.0)
        if pdf == 0:
            break
        step = (cdf - p) / pdf
        x -= step
        if x <= 0:
            x = 1e-6
        if abs(step) < 1e-9:
            break
    return x


def _norm_ppf(p):
    """Acklam's rational approximation to the standard-normal inverse CDF."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def _gammainc(a, x):
    """Regularized lower incomplete gamma P(a, x) via series / continued fraction."""
    if x < 0 or a <= 0:
        return 0.0
    if x < a + 1:
        term = 1.0 / a
        total = term
        n = a
        for _ in range(500):
            n += 1
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-12:
                break
        return total * math.exp(-x + a * math.log(x) - math.lgamma(a))
    # continued fraction for Q(a,x)
    tiny = 1e-30
    b = x + 1 - a
    c = 1 / tiny
    d = 1 / b
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-12:
            break
    q = math.exp(-x + a * math.log(x) - math.lgamma(a)) * h
    return 1 - q


def poisson_ci(observed, conf=0.95):
    """Exact two-sided Poisson CI for the mean."""
    alpha = 1 - conf
    lower = 0.0 if observed == 0 else _chi2_ppf(alpha / 2, 2 * observed) / 2
    upper = _chi2_ppf(1 - alpha / 2, 2 * (observed + 1)) / 2
    return lower, upper


# ---------------------------------------------------------------------------
# 3. SIR scenarios.
# ---------------------------------------------------------------------------
def sir(observed, person_years, rate_per_million):
    expected = person_years * rate_per_million / 1_000_000
    lo, hi = poisson_ci(observed)
    return {
        "observed": observed, "expected": round(expected, 3),
        "SIR": round(observed / expected, 1) if expected else None,
        "SIR_CI": (round(lo / expected, 1), round(hi / expected, 1)) if expected else None,
    }


SCENARIOS = [
    ("S1 central (6, 0-19, all-races 3.0/M)", 6, PY_0_19, RATE_ALL),
    ("S2 ancestry-adjusted (6, 0-19, 4.0/M)", 6, PY_0_19, RATE_WHITE),
    ("S3 peak-age (6, 10-19, 4.58/M)", 6, PY_10_19, RATE_PEAK),
    ("S4 conservative count (4, 4.0/M)", 4, PY_0_19, RATE_WHITE),
    ("S5 higher count (12, 3.0/M)", 12, PY_0_19, RATE_ALL),
    ("S6 leave-one-out (5, 4.0/M)", 5, PY_0_19, RATE_WHITE),
]


def main():
    print("=" * 78)
    print("HYPOTHETICAL Ewing sarcoma SIR scenarios — Ladera Ranch (2013-2026)")
    print("Based on UNVERIFIED public case reports and ESTIMATED population.")
    print("NOT a confirmed cluster; NOT causation. See METHODOLOGY.md.")
    print("=" * 78)
    print(f"Person-years 0-19: {PY_0_19:,}   |   Person-years 10-19: {PY_10_19:,}\n")
    for label, obs, py, rate in SCENARIOS:
        r = sir(obs, py, rate)
        print(f"{label}")
        print(f"   observed={r['observed']}  expected={r['expected']}  "
              f"SIR={r['SIR']}  95% CI={r['SIR_CI']}")
    print("\nInterpretation: Under these assumptions the reported count exceeds statistical")
    print("expectation and intervals sit above 1 — a pattern that WARRANTS INVESTIGATION.")
    print("It does NOT prove a cluster: counts are unverified/media-ascertained, the boundary")
    print("was drawn around the cases (multiple-comparison bias), residence-at-report may")
    print("differ from the etiologic window, and numbers are tiny (compare S4 vs S5). A formal")
    print("registry-based individual-level analysis would be required.")


if __name__ == "__main__":
    main()
