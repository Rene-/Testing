// JavaScript port of model.py — the ratings-based Poisson model
// (Dyte & Clarke style). The math mirrors the Python implementation exactly:
//
//   lambda_for = exp(BASE + RATING_K * (R_for - R_against) + HOME_ADV * host)
//   goals ~ Poisson(lambda)
//
// Each team's goals are independent Poisson variables driven by the FIFA
// rating gap plus a host-nation advantage.

export const BASE = Math.log(1.35); // ~1.35 expected goals for an even match
export const RATING_K = 0.0011; // goal sensitivity per rating point
export const HOME_ADV = 0.3; // additive log-goals boost for the host

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

export function expectedGoals(ratingFor, ratingAgainst, home = false) {
  let logLambda = BASE + RATING_K * (ratingFor - ratingAgainst);
  if (home) logLambda += HOME_ADV;
  return Math.exp(logLambda);
}

// Run `n` simulations of a single fixture and aggregate the results.
export function simulateFixture(home, away, n = 10000, opts = {}) {
  const { seed = null, homeIsHost = false } = opts;
  const rng = makeRng(seed);

  let homeWins = 0;
  let draws = 0;
  let awayWins = 0;
  let homeGoalsTotal = 0;
  let awayGoalsTotal = 0;
  const scorelines = new Map();

  const lamHome = expectedGoals(home.rating, away.rating, homeIsHost);
  const lamAway = expectedGoals(away.rating, home.rating, false);

  for (let i = 0; i < n; i++) {
    const hg = poisson(lamHome, rng);
    const ag = poisson(lamAway, rng);
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
