# World Cup Match Simulator — Ratings-Based Poisson Model

A small, dependency-free Python system that simulates World Cup matches using a
**ratings-based Poisson model**, and runs **1000 simulations** by default.

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
`model.py` are calibrated for the modern FIFA points scale (~1100–1900) and
are exposed as constructor arguments so you can re-calibrate freely.

## Usage

Requires only Python 3.10+ (standard library — no installs).

```bash
# Simulate one fixture 1000 times: win/draw/loss probabilities + scorelines
python3 main.py --home Argentina --away France --runs 1000

# Simulate 1000 random matchups across the field: batch statistics
python3 main.py --batch --runs 1000

# Reproducible run
python3 main.py --home Brazil --away Ghana --seed 42

# List available teams and ratings
python3 main.py --list-teams
```

### Example output

```
Ratings-based Poisson model  —  1000 simulations
Argentina (rating 1886) vs France (rating 1859)
--------------------------------------------------------
Argentina win                39.1%  (391)
Draw                         24.9%  (249)
France win                   36.0%  (360)
--------------------------------------------------------
Avg goals: Argentina 1.34  -  1.28 France
```

## Files

| File           | Purpose                                                        |
|----------------|----------------------------------------------------------------|
| `model.py`     | The Poisson model + Poisson sampler + single-match simulation. |
| `teams.py`     | Team ratings and groups (edit to use your own data).           |
| `simulator.py` | Monte-Carlo drivers: repeat-a-fixture and random-batch.        |
| `main.py`      | Command-line interface (defaults to 1000 runs).                |
| `test_model.py`| Tests (run `python3 test_model.py`).                           |

## Tests

```bash
python3 test_model.py        # stdlib runner, or:
pytest test_model.py         # if pytest is installed
```
