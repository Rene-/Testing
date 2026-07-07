"""
Monte Carlo simulation driver.

Runs many matches through the ratings-based Poisson model and aggregates the
results into probabilities and goal statistics.
"""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass, field

from model import MatchResult, PoissonModel
from teams import HOSTS, TEAMS, Team


@dataclass
class FixtureStats:
    """Aggregated statistics for repeated simulation of one fixture."""

    home: str
    away: str
    n: int
    home_wins: int = 0
    draws: int = 0
    away_wins: int = 0
    home_goals_total: int = 0
    away_goals_total: int = 0
    scorelines: Counter = field(default_factory=Counter)

    def add(self, r: MatchResult) -> None:
        if r.outcome == "home":
            self.home_wins += 1
        elif r.outcome == "away":
            self.away_wins += 1
        else:
            self.draws += 1
        self.home_goals_total += r.home_goals
        self.away_goals_total += r.away_goals
        self.scorelines[(r.home_goals, r.away_goals)] += 1

    @property
    def p_home(self) -> float:
        return self.home_wins / self.n

    @property
    def p_draw(self) -> float:
        return self.draws / self.n

    @property
    def p_away(self) -> float:
        return self.away_wins / self.n

    @property
    def avg_home_goals(self) -> float:
        return self.home_goals_total / self.n

    @property
    def avg_away_goals(self) -> float:
        return self.away_goals_total / self.n

    def most_likely_scorelines(self, top: int = 5) -> list[tuple[tuple[int, int], int]]:
        return self.scorelines.most_common(top)


def _rating(team: Team, source: str) -> float:
    if source == "live" and team.live is not None:
        return team.live
    return team.rating


def simulate_fixture(
    model: PoissonModel,
    home: Team,
    away: Team,
    n: int = 1000,
    rating_source: str = "official",
    neutral: bool = False,
) -> FixtureStats:
    """Simulate the same fixture ``n`` times to estimate its distribution.

    Host advantage applies when the home team is a co-host — pass
    ``neutral=True`` when a co-host is playing outside its own country
    (e.g. Canada's 2026 R16 tie was in Houston).
    """
    stats = FixtureStats(home=home.name, away=away.name, n=n)
    host_advantage = home.name in HOSTS and not neutral
    rh, ra = _rating(home, rating_source), _rating(away, rating_source)
    for _ in range(n):
        result = model.simulate_match(
            home.name, rh, away.name, ra, home_is_host=host_advantage
        )
        stats.add(result)
    return stats


@dataclass
class BatchStats:
    """Aggregated statistics for a batch of distinct random matchups."""

    n: int = 0
    home_wins: int = 0
    draws: int = 0
    away_wins: int = 0
    total_goals: int = 0
    results: list[MatchResult] = field(default_factory=list)

    def add(self, r: MatchResult) -> None:
        self.n += 1
        if r.outcome == "home":
            self.home_wins += 1
        elif r.outcome == "away":
            self.away_wins += 1
        else:
            self.draws += 1
        self.total_goals += r.home_goals + r.away_goals
        self.results.append(r)

    @property
    def avg_goals_per_match(self) -> float:
        return self.total_goals / self.n if self.n else 0.0


def simulate_random_matches(
    model: PoissonModel,
    n: int = 1000,
    teams: list[Team] | None = None,
    seed: int | None = None,
) -> BatchStats:
    """Simulate ``n`` matches between randomly drawn pairs of teams."""
    pool = teams if teams is not None else TEAMS
    picker = random.Random(seed)
    batch = BatchStats()
    for _ in range(n):
        a, b = picker.sample(pool, 2)
        host_advantage = a.name in HOSTS
        result = model.simulate_match(
            a.name, a.rating, b.name, b.rating, home_is_host=host_advantage
        )
        batch.add(result)
    return batch


__all__ = [
    "BatchStats",
    "FixtureStats",
    "simulate_fixture",
    "simulate_random_matches",
]
