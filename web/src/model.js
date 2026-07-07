// JavaScript port of model.py — the ratings-based Poisson model
// (Dyte & Clarke style). The math mirrors the Python implementation exactly:
//
//   lambda_for = exp(BASE + RATING_K * (R_for - R_against) + HOME_ADV * host)
//   goals ~ Poisson(lambda)
//
// Each team's goals are independent Poisson variables driven by the FIFA
// rating gap plus a host-nation advantage.

// RATING_K and HOME_ADV are fitted (scripts/calibrate.py) so the implied
// expected score matches FIFA's Elo curve We = 1/(10^(-gap/600)+1), with
// HOME_ADV equivalent to the conventional +100 Elo home bonus.
export const BASE = Math.log(1.35); // ~1.35 expected goals for an even match
export const RATING_K = 0.001474; // goal sensitivity per rating point
export const HOME_ADV = 0.284; // additive log-goals boost for the host

// Seedable RNG (mulberry32) so runs are reproducible when a seed is given.
// Falls back to Math.random when no seed is provided.
export function makeRng(seed) {
  if (seed === null || seed === undefined || seed === "") {
    return Math.random;
  }
  let a = (Number(seed) >>> 0) || 1;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Sample from a Poisson distribution using Knuth's algorithm (matches model.py).
export function poisson(lam, rng) {
  if (lam <= 0) return 0;
  const target = Math.exp(-lam);
  let k = 0;
  let p = 1.0;
  while (true) {
    k += 1;
    p *= rng();
    if (p <= target) return k - 1;
  }
}

// Dixon-Coles (1997) low-score dependence correction. Negative rho shifts
// probability onto 0-0 and 1-1 draws, matching observed low-score rates.
export const RHO = -0.1;
const MAX_GOALS = 12;

function tau(x, y, lamH, lamA, rho) {
  if (x === 0 && y === 0) return 1 - lamH * lamA * rho;
  if (x === 0 && y === 1) return 1 + lamH * rho;
  if (x === 1 && y === 0) return 1 + lamA * rho;
  if (x === 1 && y === 1) return 1 - rho;
  return 1;
}

// Joint P(home=i, away=j) grid with the Dixon-Coles adjustment, renormalised.
export function scoreGrid(lamH, lamA, rho = RHO) {
  const n = MAX_GOALS + 1;
  const ph = [];
  const pa = [];
  let fh = 1;
  let fa = 1;
  for (let i = 0; i < n; i++) {
    if (i > 0) {
      fh *= i;
      fa *= i;
    }
    ph.push((Math.exp(-lamH) * lamH ** i) / fh);
    pa.push((Math.exp(-lamA) * lamA ** i) / fa);
  }
  const grid = [];
  let total = 0;
  for (let i = 0; i < n; i++) {
    const row = [];
    for (let j = 0; j < n; j++) {
      const p = ph[i] * pa[j] * tau(i, j, lamH, lamA, rho);
      row.push(p);
      total += p;
    }
    grid.push(row);
  }
  return grid.map((row) => row.map((p) => p / total));
}

function sampleGrid(grid, rng) {
  const u = rng();
  let acc = 0;
  for (let i = 0; i < grid.length; i++) {
    for (let j = 0; j < grid[i].length; j++) {
      acc += grid[i][j];
      if (u <= acc) return [i, j];
    }
  }
  return [MAX_GOALS, MAX_GOALS];
}

export function expectedGoals(ratingFor, ratingAgainst, home = false) {
  let logLambda = BASE + RATING_K * (ratingFor - ratingAgainst);
  if (home) logLambda += HOME_ADV;
  return Math.exp(logLambda);
}

// Run `n` simulations of a single fixture and aggregate the results.
// opts.rho controls the Dixon-Coles correction (0 = independent Poisson).
export function simulateFixture(home, away, n = 10000, opts = {}) {
  const { seed = null, homeIsHost = false, rho = RHO } = opts;
  const rng = makeRng(seed);

  let homeWins = 0;
  let draws = 0;
  let awayWins = 0;
  let homeGoalsTotal = 0;
  let awayGoalsTotal = 0;
  const scorelines = new Map();

  const lamHome = expectedGoals(home.rating, away.rating, homeIsHost);
  const lamAway = expectedGoals(away.rating, home.rating, false);
  const grid = rho === 0 ? null : scoreGrid(lamHome, lamAway, rho);

  for (let i = 0; i < n; i++) {
    let hg, ag;
    if (grid) {
      [hg, ag] = sampleGrid(grid, rng);
    } else {
      hg = poisson(lamHome, rng);
      ag = poisson(lamAway, rng);
    }
    if (hg > ag) homeWins++;
    else if (ag > hg) awayWins++;
    else draws++;
    homeGoalsTotal += hg;
    awayGoalsTotal += ag;
    const key = `${hg}-${ag}`;
    scorelines.set(key, (scorelines.get(key) || 0) + 1);
  }

  const topScorelines = [...scorelines.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([score, count]) => ({ score, count, prob: count / n }));

  return {
    n,
    home: home.name,
    away: away.name,
    homeWins,
    draws,
    awayWins,
    pHome: homeWins / n,
    pDraw: draws / n,
    pAway: awayWins / n,
    avgHomeGoals: homeGoalsTotal / n,
    avgAwayGoals: awayGoalsTotal / n,
    lamHome,
    lamAway,
    topScorelines,
  };
}
