# World Cup Match Simulator — Ratings-Based Poisson Model

A small, dependency-free Python system that simulates World Cup matches using a
**ratings-based Poisson model**, and runs **10,000 simulations** by default.

## The model

The number of goals each team scores in a match is treated as an *independent*
Poisson random variable whose mean (`lambda`) is driven by the FIFA-rating gap
between the teams plus a host-nation advantage:

```
lambda_A = exp( BASE + RATING_K * (R_A - R_B) + HOME_ADV * H_A )
lambda_B = exp( BASE + RATING_K * (R_B - R_A) + HOME_ADV * H_B )

goals_A ~ Poisson(lambda_A)
goals_B ~ Poisson(lambda_B)
```

`R_x` is a team's FIFA rating and `H_x` is 1 for the host nation, else 0.

### A note on attribution

The request referenced *"David Clement's model."* The canonical, match-by-match
*simulatable* "ratings based Poisson model for World Cup soccer simulation" in
the literature is by **Dyte & Clarke** (*Journal of the Operational Research
Society*, 2000) — that is the model implemented here, since "simulate 1000
matches" is exactly what a Monte-Carlo Poisson model is built for. (A
similarly-named *Joachim Klement* econometric model exists, but it predicts a
single tournament winner from socio-economic factors rather than simulating
individual match scores, so it does not fit "simulate 1000 matches.")

The coefficients reproduce the *structure* of the Dyte & Clarke model.
Their original constants used the pre-1999 FIFA scale; the defaults in
`model.py` are **Elo-anchored**: `scripts/calibrate.py` fits `RATING_K` so the
model's implied expected score `P(win) + 0.5·P(draw)` matches FIFA's own Elo
curve `We = 1/(10^(−gap/600)+1)` (the modern FIFA ranking is Elo-based), and
fits `HOME_ADV` to the conventional +100 Elo home bonus. All three constants
remain constructor arguments so you can re-fit freely.

## Usage

Requires only Python 3.10+ (standard library — no installs).

```bash
# Simulate one fixture 10,000 times: win/draw/loss probabilities + scorelines
python3 main.py --home Argentina --away France

# Simulate 10,000 random matchups across the field: batch statistics
python3 main.py --batch

# Change the simulation count
python3 main.py --home Argentina --away France --runs 1000

# Reproducible run
python3 main.py --home Brazil --away Ghana --seed 42

# List available teams and ratings
python3 main.py --list-teams
```

### Example output

```
Ratings-based Poisson model  —  10000 simulations
Argentina (rating 1886) vs France (rating 1859)
--------------------------------------------------------
Argentina win                38.4%  (3841)
Draw                         26.2%  (2617)
France win                   35.4%  (3542)
--------------------------------------------------------
Avg goals: Argentina 1.39  -  1.31 France
```

## Backtest against the 2026 Round of 16

`scripts/backtest.py` scores model variants against the actual 2026 World Cup
Round of 16 (8 matches, 90-minute results, exact grid probabilities):

| Variant                          | Brier | Log loss | Accuracy |
|----------------------------------|-------|----------|----------|
| Uniform ⅓ baseline               | 0.667 | 1.099    | –        |
| Legacy hand-set coefficients     | 0.532 | 0.910    | 5/8      |
| **Elo-anchored (default)**       | **0.496** | **0.863** | 5/8 |
| Elo-anchored + live ratings      | 0.500 | 0.865    | 5/8      |
| Elo-anchored + Dixon–Coles −0.10 | 0.506 | 0.876    | 5/8      |

Findings (n=8, so treat differences cautiously):
- Every variant clearly beats the uniform baseline — the ratings carry signal.
- The Elo-anchored calibration beats the legacy hand-set coefficients on both
  Brier and log loss; it is the default.
- Live in-tournament ratings performed the same as the official 11-June
  points; both are supported (`--ratings live`).
- The Dixon–Coles draw correction did not help on this knockout sample
  (1 draw in 8 matches); the default is `rho = 0`, with `--rho -0.1`
  available.
- The two modal misses were Norway beating Brazil (a genuine upset) and
  Belgium 4–1 over the USA (host advantage overestimated on this occasion).
- Venue matters for host advantage: Canada's R16 tie was in Houston, so no
  home boost applied (`--neutral` covers such cases).

## Files

| File           | Purpose                                                        |
|----------------|----------------------------------------------------------------|
| `model.py`     | The Poisson model + Poisson sampler + single-match simulation. |
| `teams.py`     | Team ratings and groups (edit to use your own data).           |
| `simulator.py` | Monte-Carlo drivers: repeat-a-fixture and random-batch.        |
| `main.py`      | Command-line interface (defaults to 10,000 runs).              |
| `test_model.py`| Tests (run `python3 test_model.py`).                           |
| `web/`         | React front end (browser UI; see `web/README.md`).             |

## Tests

```bash
python3 test_model.py        # stdlib runner, or:
pytest test_model.py         # if pytest is installed
```
