"""Tests for the ratings-based Poisson World Cup simulator."""

from __future__ import annotations

import math

from model import PoissonModel, _poisson
from simulator import simulate_fixture, simulate_random_matches
from teams import by_name
import random


def test_poisson_mean_is_close():
    rng = random.Random(42)
    n = 50_000
    lam = 1.5
    total = sum(_poisson(lam, rng) for _ in range(n))
    assert abs(total / n - lam) < 0.05


def test_poisson_zero_lambda():
    rng = random.Random(0)
    assert all(_poisson(0, rng) == 0 for _ in range(100))


def test_expected_goals_symmetry():
    m = PoissonModel()
    # Equal ratings, neutral venue -> equal expected goals == exp(base).
    eg = m.expected_goals(1600, 1600)
    assert math.isclose(eg, math.exp(m.base), rel_tol=1e-9)


def test_stronger_team_scores_more():
    m = PoissonModel()
    strong = m.expected_goals(1850, 1450)
    weak = m.expected_goals(1450, 1850)
    assert strong > weak


def test_home_advantage_increases_goals():
    m = PoissonModel()
    away = m.expected_goals(1600, 1600, home=False)
    home = m.expected_goals(1600, 1600, home=True)
    assert home > away


def test_reproducible_with_seed():
    a = simulate_fixture(PoissonModel(seed=7), by_name("Brazil"), by_name("Ghana"), n=500)
    b = simulate_fixture(PoissonModel(seed=7), by_name("Brazil"), by_name("Ghana"), n=500)
    assert (a.home_wins, a.draws, a.away_wins) == (b.home_wins, b.draws, b.away_wins)


def test_probabilities_sum_to_one():
    s = simulate_fixture(PoissonModel(seed=1), by_name("Spain"), by_name("Iran"), n=1000)
    assert math.isclose(s.p_home + s.p_draw + s.p_away, 1.0, rel_tol=1e-9)
    assert s.n == 1000


def test_favourite_wins_more_often():
    s = simulate_fixture(PoissonModel(seed=3), by_name("Argentina"), by_name("Saudi Arabia"), n=2000)
    assert s.p_home > s.p_away


def test_batch_runs_requested_count():
    batch = simulate_random_matches(PoissonModel(seed=5), n=1000, seed=5)
    assert batch.n == 1000
    assert batch.home_wins + batch.draws + batch.away_wins == 1000
    assert batch.avg_goals_per_match > 0


if __name__ == "__main__":
    import sys
    import traceback

    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    sys.exit(1 if failures else 0)
