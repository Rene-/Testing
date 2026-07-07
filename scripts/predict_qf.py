"""
Pre-registered quarter-final forecasts for the 2026 World Cup.

Run BEFORE the quarter-finals are played; the commit timestamp is the
pre-registration record. All four QFs are on neutral US soil (every
co-host was eliminated in the Round of 16), so no host advantage applies.

Emits forecasts from the backtest's model variants so each can be scored
against reality afterwards by scripts/backtest.py.

Run:  python3 scripts/predict_qf.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model import PoissonModel
from teams import by_name

# (home-listed team, away, date, venue) — all neutral venues.
# QF4's opponent depends on Switzerland-Colombia (in extra time at
# pre-registration time), so both scenarios are forecast.
QUARTERFINALS = [
    ("France", "Morocco", "Jul 9", "Boston"),
    ("Spain", "Belgium", "Jul 10", "Los Angeles"),
    ("Norway", "England", "Jul 11", "Miami"),
    ("Argentina", "Switzerland", "Jul 12", "Kansas City"),
    ("Argentina", "Colombia", "Jul 12", "Kansas City"),
]

VARIANTS = [
    ("Elo-anchored, official (default)", PoissonModel(), "rating"),
    ("Elo-anchored, live", PoissonModel(), "live"),
    ("Elo-anchored, live, DC rho=-0.10", PoissonModel(rho=-0.10), "live"),
]


def team_rating(name: str, attr: str) -> float:
    t = by_name(name)
    if attr == "live" and t.live is not None:
        return t.live
    return t.rating


def main() -> None:
    for vname, model, attr in VARIANTS:
        print(f"\n=== {vname} ===")
        print(f"{'fixture':<28} {'p(home)':>8} {'p(draw)':>8} {'p(away)':>8} "
              f"{'xG':>12}")
        for home, away, date, venue in QUARTERFINALS:
            rh, ra = team_rating(home, attr), team_rating(away, attr)
            lam_h = model.expected_goals(rh, ra, home=False)
            lam_a = model.expected_goals(ra, rh, home=False)
            pw, pd, pl = model.outcome_probabilities(lam_h, lam_a)
            print(f"{home} v {away:<14} {pw:>8.1%} {pd:>8.1%} {pl:>8.1%} "
                  f"{lam_h:>5.2f}-{lam_a:.2f}  ({date}, {venue})")


if __name__ == "__main__":
    main()
