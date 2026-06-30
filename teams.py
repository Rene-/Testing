"""
Team data for the simulation.

Ratings are approximate FIFA points (modern scale) for leading national
teams, grouped to resemble a World Cup draw. They are only inputs to the
model; swap in your own ratings/groups freely.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Team:
    name: str
    rating: float
    group: str


# Approximate FIFA points for a representative World Cup field.
TEAMS: list[Team] = [
    Team("Argentina", 1886, "A"),
    Team("Mexico", 1687.48, "A"),  # FIFA points, 11 Jun 2026 (rank 14)
    Team("Poland", 1546, "A"),
    Team("Saudi Arabia", 1419, "A"),

    Team("France", 1859, "B"),
    Team("Senegal", 1630, "B"),
    Team("Japan", 1652, "B"),
    Team("Canada", 1531, "B"),

    Team("Spain", 1854, "C"),
    Team("Croatia", 1716, "C"),
    Team("Morocco", 1694, "C"),
    Team("South Korea", 1575, "C"),

    Team("England", 1819, "D"),
    Team("Netherlands", 1745, "D"),
    Team("USA", 1648, "D"),
    Team("Australia", 1488, "D"),

    Team("Brazil", 1776, "E"),
    Team("Portugal", 1761, "E"),
    Team("Switzerland", 1644, "E"),
    Team("Ghana", 1450, "E"),

    Team("Belgium", 1737, "F"),
    Team("Germany", 1717, "F"),
    Team("Ecuador", 1598.52, "F"),  # FIFA points, 11 Jun 2026 (rank 23)
    Team("Qatar", 1400, "F"),

    Team("Italy", 1718, "G"),
    Team("Uruguay", 1639, "G"),
    Team("Colombia", 1690, "G"),
    Team("Nigeria", 1503, "G"),

    Team("Denmark", 1666, "H"),
    Team("Mexico B", 1600, "H"),
    Team("Serbia", 1549, "H"),
    Team("Iran", 1500, "H"),
]

# Host nation gets the home-advantage term in the model.
HOST = "USA"


def by_name(name: str) -> Team:
    for t in TEAMS:
        if t.name == name:
            return t
    raise KeyError(f"Unknown team: {name!r}")


def rating_of(name: str) -> float:
    return by_name(name).rating
