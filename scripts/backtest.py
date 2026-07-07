"""
Backtest model variants against the actual 2026 World Cup Round of 16.

For each variant we compute EXACT win/draw/loss probabilities from the
model's score grid (no Monte Carlo noise) and score them against the
90-minute results with standard forecast metrics:

  * Brier score  — mean squared error over the 3-way outcome (lower = better)
  * Log loss     — -mean ln(probability assigned to what happened)
  * Accuracy     — how often the modal prediction matched the outcome
  * Goals MAE    — mean absolute error of each team's expected goals

Baselines to beat: the uniform forecast (1/3, 1/3, 1/3) scores Brier 0.667,
log loss 1.099. A model must beat these to carry any information.

Run:  python3 scripts/backtest.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model import PoissonModel

# --- Ratings: official FIFA points (11 Jun 2026) and live points (early
# --- Jul 2026, pre-R16). None = not yet verified against a source; the
# --- script refuses to run while any None remains.
RATINGS: dict[str, dict[str, float | None]] = {
    #                 official   live
    "Morocco":     {"official": 1756.94, "live": 1788.86},
    "Canada":      {"official": 1559.48, "live": 1571.34},
    "France":      {"official": 1870.70, "live": 1916.24},
    "Paraguay":    {"official": 1505.35, "live": 1542.48},
    "Norway":      {"official": 1557.44, "live": 1617.67},
    "Brazil":      {"official": 1765.34, "live": 1804.92},
    "England":     {"official": 1840.46, "live": 1850.97},
    "Mexico":      {"official": 1687.48, "live": 1754.30},
    "Spain":       {"official": 1874.71, "live": 1892.28},
    "Portugal":    {"official": 1767.85, "live": 1787.85},
    # Belgium's exact official 11-Jun total was not published in accessible
    # sources (rank 9 confirmed); 1733.93 is their earliest in-tournament
    # live figure and the closest available proxy for the official baseline.
    "Belgium":     {"official": 1733.93, "live": 1756.51},
    "USA":         {"official": 1671.23, "live": 1690.33},
    "Argentina":   {"official": 1877.27, "live": 1913.71},
    "Egypt":       {"official": 1562.37, "live": 1597.04},
    "Switzerland": {"official": 1650.00, "live": 1696.30},
    "Colombia":    {"official": 1698.35, "live": 1739.89},
}

# --- Round of 16 fixtures with 90-minute results.
# "home" is listed first; host=True when that team is a co-host playing on
# home soil. Scores must be the 90-minute score (knockout draws then go to
# ET/pens). score=None = result not yet verified; the script refuses to run.
# All seven completed matches ended in regulation (90' score == final).
# Canada-Morocco was played in Houston, USA -> Canada NOT on home soil.
# USA-Belgium was in Seattle (USA at home); Mexico-England at the Azteca.
FIXTURES: list[dict] = [
    {"home": "Canada", "away": "Morocco", "score": (0, 3), "host": False},
    {"home": "France", "away": "Paraguay", "score": (1, 0), "host": False},
    {"home": "Norway", "away": "Brazil", "score": (2, 1), "host": False},
    {"home": "Mexico", "away": "England", "score": (2, 3), "host": True},
    {"home": "Spain", "away": "Portugal", "score": (1, 0), "host": False},
    {"home": "USA", "away": "Belgium", "score": (1, 4), "host": True},
    {"home": "Argentina", "away": "Egypt", "score": (3, 2), "host": False},
    # 0-0 after 90 minutes (went to extra time; 90' score is what we grade).
    {"home": "Switzerland", "away": "Colombia", "score": (0, 0), "host": False},

    # --- Quarter-finals (all neutral US venues; co-hosts eliminated). ------
    # Forecasts pre-registered in scripts/predict_qf.py before kickoff.
    # Fill 90-minute scores as the games are played; QF4's opponent comes
    # from the Switzerland-Colombia winner (delete the loser's line).
    {"home": "France", "away": "Morocco", "score": None, "host": False},
    {"home": "Spain", "away": "Belgium", "score": None, "host": False},
    {"home": "Norway", "away": "England", "score": None, "host": False},
    {"home": "Argentina", "away": "Switzerland", "score": None, "host": False},
    {"home": "Argentina", "away": "Colombia", "score": None, "host": False},
]


def _validate_data() -> None:
    """Refuse to run on unverified ratings; skip unplayed fixtures loudly."""
    missing = [t for t, r in RATINGS.items() if r["official"] is None or r["live"] is None]
    if missing:
        raise SystemExit(f"Unverified ratings remain, refusing to run: {missing}")
    pending = [f for f in FIXTURES if f["score"] is None]
    for f in pending:
        print(f"NOTE: skipping unplayed fixture {f['home']} vs {f['away']}\n")
    FIXTURES[:] = [f for f in FIXTURES if f["score"] is not None]


def outcome_index(hg: int, ag: int) -> int:
    """0 = home win, 1 = draw, 2 = away win."""
    if hg > ag:
        return 0
    if hg == ag:
        return 1
    return 2


def evaluate(name: str, model: PoissonModel, rating_key: str) -> dict:
    brier = logloss = goals_err = 0.0
    correct = 0
    rows = []
    for fx in FIXTURES:
        rh = RATINGS[fx["home"]][rating_key]
        ra = RATINGS[fx["away"]][rating_key]
        lam_h = model.expected_goals(rh, ra, home=fx["host"])
        lam_a = model.expected_goals(ra, rh, home=False)
        probs = model.outcome_probabilities(lam_h, lam_a)
        actual = outcome_index(*fx["score"])
        onehot = [1.0 if i == actual else 0.0 for i in range(3)]

        brier += sum((p - o) ** 2 for p, o in zip(probs, onehot))
        logloss += -math.log(max(probs[actual], 1e-12))
        goals_err += (abs(lam_h - fx["score"][0]) + abs(lam_a - fx["score"][1])) / 2
        modal = max(range(3), key=lambda i: probs[i])
        correct += modal == actual
        rows.append((fx, probs, actual, modal))

    n = len(FIXTURES)
    return {
        "name": name,
        "brier": brier / n,
        "logloss": logloss / n,
        "accuracy": correct / n,
        "goals_mae": goals_err / n,
        "rows": rows,
    }


VARIANTS = [
    ("V0 legacy hand-set, official", PoissonModel(rating_k=0.0011, home_adv=0.30), "official"),
    ("V1 Elo-anchored, official", PoissonModel(), "official"),
    ("V2 Elo-anchored, live", PoissonModel(), "live"),
    ("V3 Elo-anchored, live, DC rho=-0.10", PoissonModel(rho=-0.10), "live"),
]


def main() -> None:
    _validate_data()
    print(f"{'variant':<38} {'Brier':>7} {'LogLoss':>8} {'Acc':>6} {'xG MAE':>7}")
    print("-" * 72)
    print(f"{'uniform 1/3 baseline':<38} {0.667:>7.3f} {1.099:>8.3f} {'-':>6} {'-':>7}")
    results = []
    for name, model, key in VARIANTS:
        r = evaluate(name, model, key)
        results.append(r)
        print(
            f"{r['name']:<38} {r['brier']:>7.3f} {r['logloss']:>8.3f} "
            f"{r['accuracy']:>6.0%} {r['goals_mae']:>7.2f}"
        )

    # Per-match detail for the best variant by log loss.
    best = min(results, key=lambda r: r["logloss"])
    print(f"\nPer-match detail — {best['name']}:")
    labels = ["home win", "draw", "away win"]
    for fx, probs, actual, modal in best["rows"]:
        tick = "HIT " if modal == actual else "miss"
        print(
            f"  [{tick}] {fx['home']:<12} {fx['score'][0]}-{fx['score'][1]} "
            f"{fx['away']:<12} p(W/D/L)="
            f"{probs[0]:.2f}/{probs[1]:.2f}/{probs[2]:.2f}"
            f"  actual: {labels[actual]}"
        )

    # Rho sensitivity sweep on the best rating source.
    print("\nDixon-Coles rho sweep (Elo-anchored, live ratings):")
    for rho in (0.0, -0.05, -0.10, -0.15, -0.20):
        r = evaluate(f"rho={rho:+.2f}", PoissonModel(rho=rho), "live")
        print(f"  rho={rho:+.2f}  Brier {r['brier']:.3f}  LogLoss {r['logloss']:.3f}")


if __name__ == "__main__":
    main()
