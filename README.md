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

## Backtest against the 2026 knockout rounds

`scripts/backtest.py` scores model variants against the actual 2026 World Cup
Round of 16 + quarter-finals (12 matches, 90-minute results, exact grid
probabilities). Quarter-final forecasts were pre-registered before kickoff
(`scripts/predict_qf.py`, committed 7 July).

| Variant                          | Brier | Log loss | Accuracy |
|----------------------------------|-------|----------|----------|
| Uniform ⅓ baseline               | 0.667 | 1.099    | –        |
| Legacy hand-set coefficients     | 0.585 | 0.980    | 7/12     |
| Elo-anchored, official           | 0.567 | 0.952    | 7/12     |
| Elo-anchored, live               | 0.561 | 0.944    | 7/12     |
| **Elo-anchored, live, DC −0.10** | **0.560** | **0.940** | 7/12 |

Findings (n=12; only the legacy-vs-anchored gap is decisive):
- The Elo-anchored calibration beats the legacy hand-set coefficients in
  BOTH the 8-match and 12-match samples — the one robust conclusion.
- The Dixon–Coles verdict flipped with the sample: it hurt on 8 matches
  (1 draw) and helps on 12 (3 draws, 25% — right at the model's forecast
  rate). With the literature prior for negative rho now weakly confirmed,
  the CLI default is `--rho -0.10` (the `PoissonModel` class default stays
  0 = pure Dyte–Clarke; the rho sweep is nearly flat from −0.05 to −0.20).
- Live ratings edged official ratings on the extended sample (0.944 vs
  0.952) — within noise, but fresher information costs nothing when
  available (`--ratings live`; teams without a live figure fall back).
- Modal accuracy understates draw-aware models: no model ever makes "draw"
  its modal pick, and all five misses on the extended sample include the
  three 90-minute draws. Log loss is the honest metric.
- Other learnings: Norway beating Brazil was a genuine upset; Belgium 4–1
  USA showed host advantage is no guarantee; venue must be checked per
  match (Canada's "home" R16 tie was in Houston — `--neutral`).

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
