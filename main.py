#!/usr/bin/env python3
"""
Command-line entry point for the World Cup match simulator.

Examples
--------
Simulate one fixture 10,000 times (probabilities + likely scorelines):

    python main.py --home Argentina --away France

Simulate 10,000 random matchups across the field (batch statistics):

    python main.py --batch

Both default to 10,000 runs. Use --runs to change (e.g. --runs 1000).
"""

from __future__ import annotations

import argparse

from model import PoissonModel
from simulator import simulate_fixture, simulate_random_matches
from teams import TEAMS, by_name


def _pct(x: float) -> str:
    return f"{x * 100:5.1f}%"


def run_fixture(args: argparse.Namespace) -> None:
    model = PoissonModel(seed=args.seed)
    home = by_name(args.home)
    away = by_name(args.away)
    stats = simulate_fixture(model, home, away, n=args.runs)

    print(f"\nRatings-based Poisson model  —  {stats.n} simulations")
    print(f"{home.name} (rating {home.rating:g}) vs {away.name} (rating {away.rating:g})")
    print("-" * 56)
    print(f"{home.name + ' win':<28}{_pct(stats.p_home)}  ({stats.home_wins})")
    print(f"{'Draw':<28}{_pct(stats.p_draw)}  ({stats.draws})")
    print(f"{away.name + ' win':<28}{_pct(stats.p_away)}  ({stats.away_wins})")
    print("-" * 56)
    print(f"Avg goals: {home.name} {stats.avg_home_goals:.2f}  -  "
          f"{stats.avg_away_goals:.2f} {away.name}")
    print("\nMost likely scorelines:")
    for (hg, ag), count in stats.most_likely_scorelines(top=6):
        print(f"  {home.name} {hg}-{ag} {away.name:<14} {_pct(count / stats.n)}")
    print()


def run_batch(args: argparse.Namespace) -> None:
    model = PoissonModel(seed=args.seed)
    batch = simulate_random_matches(model, n=args.runs, seed=args.seed)

    print(f"\nRatings-based Poisson model  —  {batch.n} random matches")
    print("-" * 56)
    print(f"{'Home/first-team wins':<28}{_pct(batch.home_wins / batch.n)}  ({batch.home_wins})")
    print(f"{'Draws':<28}{_pct(batch.draws / batch.n)}  ({batch.draws})")
    print(f"{'Away/second-team wins':<28}{_pct(batch.away_wins / batch.n)}  ({batch.away_wins})")
    print("-" * 56)
    print(f"Average goals per match: {batch.avg_goals_per_match:.2f}")
    print("\nSample of simulated results:")
    for r in batch.results[:10]:
        print(f"  {r}")
    print()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Simulate World Cup matches with a ratings-based Poisson model.")
    p.add_argument("--runs", type=int, default=10000, help="number of simulations (default: 10000)")
    p.add_argument("--seed", type=int, default=None, help="random seed for reproducibility")
    p.add_argument("--home", default="Argentina", help="first team (fixture mode)")
    p.add_argument("--away", default="France", help="second team (fixture mode)")
    p.add_argument("--batch", action="store_true",
                   help="simulate random matchups across the field instead of one fixture")
    p.add_argument("--list-teams", action="store_true", help="list available teams and exit")
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.list_teams:
        for t in sorted(TEAMS, key=lambda x: -x.rating):
            print(f"  {t.name:<16} {t.rating:>5g}  (group {t.group})")
        return
    if args.batch:
        run_batch(args)
    else:
        run_fixture(args)


if __name__ == "__main__":
    main()
