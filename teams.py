"""
Team data for the simulation.

``rating``  — official FIFA points from the 11 June 2026 update (the last
              official pre-World-Cup release) where marked; otherwise an
              approximate placeholder.
``live``    — unofficial live FIFA points as of early July 2026 (reflecting
              group stage + Round of 32 results), where a sourced figure
              exists; None otherwise. Select with --ratings live.

Verified figures were collected from FIFA and match-preview coverage
(World Soccer Talk, Bolavip, ESPN and others) on 7 July 2026.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Team:
    name: str
    rating: float
    group: str
    live: float | None = None


TEAMS: list[Team] = [
    # --- Round of 16 participants: official 11 Jun 2026 + live early-Jul ---
    Team("Argentina", 1877.27, "A", live=1913.71),   # rank 1 -> live 2
    Team("Mexico", 1687.48, "A", live=1754.30),      # rank 14 -> live 10
    Team("France", 1870.70, "B", live=1916.24),      # rank 3 -> live 1
    Team("Canada", 1559.48, "B", live=1571.34),      # rank 30 -> live 30
    Team("Spain", 1874.71, "C", live=1892.28),       # rank 2 -> live 3
    Team("Morocco", 1756.94, "C", live=1788.86),     # rank 7 -> live 6
    Team("England", 1840.46, "D", live=1850.97),     # rank 4 -> live 4
    Team("USA", 1671.23, "D", live=1690.33),         # rank 17 -> live 16
    Team("Brazil", 1765.34, "E", live=1804.92),      # rank 6 -> live 5
    Team("Portugal", 1767.85, "E", live=1787.85),    # rank 5 -> live 7
    # Belgium: official 11-Jun total not published in accessible sources
    # (rank 9 confirmed); 1733.93 is their earliest in-tournament live
    # figure, used as the closest proxy for the official baseline.
    Team("Belgium", 1733.93, "F", live=1756.51),
    Team("Ecuador", 1598.52, "F", live=None),        # rank 23 (11 Jun)
    Team("Colombia", 1698.35, "G", live=1739.89),    # rank 13 -> live 11
    Team("Switzerland", 1650.00, "G", live=1696.30), # rank 19 -> live 15
    Team("Norway", 1557.44, "H", live=1617.67),      # rank 31 -> live 21
    Team("Paraguay", 1505.35, "H", live=1542.48),    # rank 41 -> live 34
    Team("Egypt", 1562.37, "I", live=1597.04),       # rank 29 -> live 24
    Team("Bosnia and Herzegovina", 1387.22, "I", live=None),  # rank 64 (11 Jun)

    # --- Other teams: approximate placeholder ratings (unverified) ---------
    Team("Poland", 1546, "J"),
    Team("Saudi Arabia", 1419, "J"),
    Team("Senegal", 1630, "J"),
    Team("Japan", 1652, "J"),
    Team("Croatia", 1716, "K"),
    Team("South Korea", 1575, "K"),
    Team("Netherlands", 1745, "K"),
    Team("Australia", 1488, "K"),
    Team("Ghana", 1450, "L"),
    Team("Germany", 1717, "L"),
    Team("Qatar", 1400, "L"),
    Team("Italy", 1718, "L"),
    Team("Uruguay", 1639, "M"),
    Team("Nigeria", 1503, "M"),
    Team("Denmark", 1666, "M"),
    Team("Serbia", 1549, "M"),
    Team("Iran", 1500, "M"),
]

# Host nations get the home-advantage term in the model — but only when the
# match is actually played in their country (2026 has three co-hosts, and
# e.g. Canada played their R16 tie in Houston with no home advantage).
HOSTS = {"USA", "Canada", "Mexico"}


def by_name(name: str) -> Team:
    for t in TEAMS:
        if t.name == name:
            return t
    raise KeyError(f"Unknown team: {name!r}")


def rating_of(name: str, source: str = "official") -> float:
    """Team rating; source='live' falls back to official when no live figure."""
    t = by_name(name)
    if source == "live" and t.live is not None:
        return t.live
    return t.rating
