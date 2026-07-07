"""
Ratings-based Poisson model for World Cup soccer simulation.

This implements the model popularised by Dyte & Clarke, "A ratings based
Poisson model for World Cup soccer simulation" (Journal of the Operational
Research Society, 2000). The user referred to it as "David Clement's model";
the canonical, match-by-match simulatable version in the literature is the
Dyte & Clarke ratings-based Poisson model, which is what is implemented here.

Core idea
---------
The number of goals scored by each team in a match is treated as an
*independent* Poisson random variable. The mean (lambda) of each team's
Poisson distribution is driven by:

    * the difference between the two teams' FIFA ratings, and
    * a venue / home-advantage term.

For a match between team A and team B:

    lambda_A = exp( BASE + RATING_K * (R_A - R_B) + HOME_ADV * H_A )
    lambda_B = exp( BASE + RATING_K * (R_B - R_A) + HOME_ADV * H_B )

    goals_A ~ Poisson(lambda_A)
    goals_B ~ Poisson(lambda_B)

where R_x is the FIFA rating of team x and H_x is 1 if team x is playing at
home (host nation) and 0 otherwise.

The coefficients below reproduce the *structure* of the Dyte & Clarke model.
Their original fitted constants used the pre-1999 FIFA rating scale; the
defaults here are anchored to the modern (post-2018, Elo-based) FIFA points
scale by scripts/calibrate.py — see the comment above the constants. All
three are exposed as constructor arguments so the model can be re-fitted.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


# --- Default calibrated coefficients (modern FIFA points scale) -------------
# RATING_K and HOME_ADV are fitted by scripts/calibrate.py so the model's
# implied expected score P(win) + 0.5*P(draw) matches FIFA's own Elo curve
# We = 1/(10^(-gap/600)+1), with HOME_ADV equivalent to the conventional
# +100 Elo home bonus. BASE is fixed to give ~2.7 total goals per match.
BASE = math.log(1.35)   # ~1.35 expected goals for an evenly matched team
RATING_K = 0.001474     # sensitivity of goals to rating difference (per point)
HOME_ADV = 0.2840       # additive log-goals boost for the host nation


@dataclass
class MatchResult:
    """Outcome of a single simulated match."""

    home: str
    away: str
    home_goals: int
    away_goals: int

    @property
    def outcome(self) -> str:
        if self.home_goals > self.away_goals:
            return "home"
        if self.home_goals < self.away_goals:
            return "away"
        return "draw"

    @property
    def winner(self) -> str | None:
        if self.outcome == "home":
            return self.home
        if self.outcome == "away":
            return self.away
        return None

    def __str__(self) -> str:
        return f"{self.home} {self.home_goals}-{self.away_goals} {self.away}"


def _poisson(lam: float, rng: random.Random) -> int:
    """Sample from a Poisson distribution using Knuth's algorithm.

    Pure-stdlib so the project has no third-party dependencies. For the
    goal-count magnitudes involved (lambda well under ~10) this is both
    exact and fast.
    """
    if lam <= 0:
        return 0
    target = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= target:
            return k - 1


class PoissonModel:
    """The ratings-based Poisson match model (Dyte & Clarke style).

    ``rho`` enables the Dixon & Coles (1997) low-score dependence
    correction: the joint probability of scores (0,0), (1,0), (0,1) and
    (1,1) is scaled by tau(x, y), which for negative rho shifts mass onto
    0-0 and 1-1 draws — fixing the independent-Poisson model's known
    underestimate of low-scoring draws. rho = 0 recovers independence.
    """

    #: Scores above this are vanishingly likely; the joint grid is truncated
    #: here and renormalised.
    MAX_GOALS = 12

    def __init__(
        self,
        base: float = BASE,
        rating_k: float = RATING_K,
        home_adv: float = HOME_ADV,
        rho: float = 0.0,
        seed: int | None = None,
    ) -> None:
        self.base = base
        self.rating_k = rating_k
        self.home_adv = home_adv
        self.rho = rho
        self.rng = random.Random(seed)

    def _tau(self, x: int, y: int, lam_h: float, lam_a: float) -> float:
        if x == 0 and y == 0:
            return 1.0 - lam_h * lam_a * self.rho
        if x == 0 and y == 1:
            return 1.0 + lam_h * self.rho
        if x == 1 and y == 0:
            return 1.0 + lam_a * self.rho
        if x == 1 and y == 1:
            return 1.0 - self.rho
        return 1.0

    def score_grid(self, lam_h: float, lam_a: float) -> list[list[float]]:
        """Joint P(home=x, away=y) grid with the Dixon-Coles adjustment."""
        n = self.MAX_GOALS + 1
        ph = [math.exp(-lam_h) * lam_h**i / math.factorial(i) for i in range(n)]
        pa = [math.exp(-lam_a) * lam_a**j / math.factorial(j) for j in range(n)]
        grid = [
            [ph[i] * pa[j] * self._tau(i, j, lam_h, lam_a) for j in range(n)]
            for i in range(n)
        ]
        total = sum(sum(row) for row in grid)
        return [[p / total for p in row] for row in grid]

    def outcome_probabilities(
        self, lam_h: float, lam_a: float
    ) -> tuple[float, float, float]:
        """Exact (p_home_win, p_draw, p_away_win) from the score grid."""
        grid = self.score_grid(lam_h, lam_a)
        win = sum(grid[i][j] for i in range(len(grid)) for j in range(i))
        draw = sum(grid[i][i] for i in range(len(grid)))
        return win, draw, 1.0 - win - draw

    def expected_goals(
        self,
        rating_for: float,
        rating_against: float,
        home: bool = False,
    ) -> float:
        """Expected goals (lambda) for a team given the rating gap and venue."""
        log_lambda = self.base + self.rating_k * (rating_for - rating_against)
        if home:
            log_lambda += self.home_adv
        return math.exp(log_lambda)

    def simulate_match(
        self,
        home_name: str,
        home_rating: float,
        away_name: str,
        away_rating: float,
        home_is_host: bool = False,
    ) -> MatchResult:
        """Simulate one match and return the scoreline.

        By convention the first team is the nominal "home" team; set
        ``home_is_host`` only for a genuine host-nation advantage (e.g. a
        World Cup host). Neutral-venue knockout games leave it False.
        """
        lam_home = self.expected_goals(home_rating, away_rating, home=home_is_host)
        lam_away = self.expected_goals(away_rating, home_rating, home=False)
        if self.rho == 0.0:
            hg, ag = _poisson(lam_home, self.rng), _poisson(lam_away, self.rng)
        else:
            hg, ag = self._sample_grid(lam_home, lam_away)
        return MatchResult(
            home=home_name, away=away_name, home_goals=hg, away_goals=ag
        )

    def _sample_grid(self, lam_h: float, lam_a: float) -> tuple[int, int]:
        """Sample a scoreline from the Dixon-Coles joint distribution."""
        key = (lam_h, lam_a)
        if not hasattr(self, "_grid_cache"):
            self._grid_cache: dict = {}
        if key not in self._grid_cache:
            self._grid_cache[key] = self.score_grid(lam_h, lam_a)
        grid = self._grid_cache[key]
        u = self.rng.random()
        acc = 0.0
        for i, row in enumerate(grid):
            for j, p in enumerate(row):
                acc += p
                if u <= acc:
                    return i, j
        return self.MAX_GOALS, self.MAX_GOALS
