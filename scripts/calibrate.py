"""
Calibrate the Poisson model's coefficients against the FIFA Elo curve.

FIFA's post-2018 "SUM" ranking is Elo-based: the expected score of a team
with rating advantage d is

    We(d) = 1 / (10 ** (-d / 600) + 1)

Since the ratings we feed the model ARE FIFA points, the Poisson model's
implied expected score  S(d) = P(win) + 0.5 * P(draw)  should agree with
We(d). This script fits:

  * RATING_K  — minimises the squared error between S(d) and We(d)
                over the rating gaps seen in practice (0..500 points).
  * HOME_ADV  — chosen so that a host playing an equal-rated opponent has
                the same expected score as a +100 Elo advantage, the
                conventional Elo home bonus.

Run:  python3 scripts/calibrate.py
"""

from __future__ import annotations

import math

BASE = math.log(1.35)  # kept fixed: total goals/match ~2.7 matches World Cup data
MAX_GOALS = 25


def poisson_pmf(lam: float, k: int) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def expected_score(lam1: float, lam2: float) -> float:
    """P(team1 wins) + 0.5 * P(draw) for independent Poisson goal counts."""
    p1 = [poisson_pmf(lam1, i) for i in range(MAX_GOALS)]
    p2 = [poisson_pmf(lam2, i) for i in range(MAX_GOALS)]
    win = sum(p1[i] * p2[j] for i in range(MAX_GOALS) for j in range(i))
    draw = sum(p1[i] * p2[i] for i in range(MAX_GOALS))
    return win + 0.5 * draw


def model_score(delta: float, k: float, home_adv: float = 0.0) -> float:
    lam1 = math.exp(BASE + k * delta + home_adv)
    lam2 = math.exp(BASE - k * delta)
    return expected_score(lam1, lam2)


def fifa_we(delta: float) -> float:
    return 1.0 / (10 ** (-delta / 600) + 1)


def fit_rating_k() -> float:
    deltas = list(range(0, 501, 25))

    def loss(k: float) -> float:
        return sum((model_score(d, k) - fifa_we(d)) ** 2 for d in deltas)

    # Coarse-to-fine grid search; loss is smooth and unimodal in this range.
    best_k, best_l = None, float("inf")
    grid = [x * 1e-4 for x in range(5, 61)]  # 0.0005 .. 0.0060
    for _ in range(3):
        for k in grid:
            l = loss(k)
            if l < best_l:
                best_k, best_l = k, l
        step = (grid[1] - grid[0]) / 10
        grid = [best_k + (i - 10) * step for i in range(21)]
    return best_k


def fit_home_adv(k: float) -> float:
    target = fifa_we(100)  # +100 Elo is the conventional home bonus

    lo, hi = 0.0, 1.5
    for _ in range(60):  # bisection on the monotone expected-score curve
        mid = (lo + hi) / 2
        if model_score(0.0, k, home_adv=mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


if __name__ == "__main__":
    k = fit_rating_k()
    h = fit_home_adv(k)
    print(f"Fitted RATING_K = {k:.6f}")
    print(f"Fitted HOME_ADV = {h:.4f}  (matches +100 Elo home bonus, "
          f"target We = {fifa_we(100):.4f})")
    print()
    print(f"{'gap':>5} {'FIFA We':>8} {'model S':>8}")
    for d in (0, 50, 100, 153, 200, 284, 400):
        print(f"{d:>5} {fifa_we(d):>8.4f} {model_score(d, k):>8.4f}")
