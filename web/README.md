# World Cup Simulator — React Front End

A single-page React app for the ratings-based Poisson match simulator. The
model is ported to JavaScript (`src/model.js`) and runs **entirely in the
browser** — no Python backend required. The math mirrors the project's
`model.py` exactly (same `BASE`, `RATING_K`, `HOME_ADV`, Knuth Poisson
sampler, and co-host set).

## Features

- Pick any two teams (dropdowns sorted by FIFA rating; ★ marks 2026 co-hosts).
- Choose the number of simulations (default 10,000) and an optional seed for
  reproducible runs.
- Host advantage auto-detects when the home team is a 2026 co-host (USA,
  Canada, Mexico) and can be toggled manually.
- Results: win/draw/loss probability bars, expected goals, and the most likely
  scorelines.

## Run it

```bash
cd web
npm install
npm run dev      # start the dev server (prints a local URL)
```

Build a static bundle:

```bash
npm run build    # outputs to web/dist/
npm run preview  # serve the production build locally
```

## Keeping data in sync

`src/teams.js` mirrors the Python `teams.py`. When you update ratings in one,
update the other so the CLI and the web app agree.
