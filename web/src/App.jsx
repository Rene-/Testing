import React, { useMemo, useState } from "react";
import { TEAMS, HOSTS, byName } from "./teams.js";
import { simulateFixture } from "./model.js";

const sortedTeams = [...TEAMS].sort((a, b) => b.rating - a.rating);

function pct(x) {
  return `${(x * 100).toFixed(1)}%`;
}

function TeamSelect({ label, value, onChange }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {sortedTeams.map((t) => (
          <option key={t.name} value={t.name}>
            {t.name} ({t.rating}){HOSTS.has(t.name) ? " ★" : ""}
          </option>
        ))}
      </select>
    </label>
  );
}

function OutcomeBar({ label, prob, count, color }) {
  return (
    <div className="bar-row">
      <span className="bar-name">{label}</span>
      <div className="bar-track">
        <div
          className="bar-fill"
          style={{ width: `${Math.max(prob * 100, 2)}%`, background: color }}
        />
      </div>
      <span className="bar-value">
        {pct(prob)} <span className="bar-count">({count})</span>
      </span>
    </div>
  );
}

export default function App() {
  const [homeName, setHomeName] = useState("Mexico");
  const [awayName, setAwayName] = useState("Ecuador");
  const [runs, setRuns] = useState(10000);
  const [seed, setSeed] = useState("");
  const [hostOverride, setHostOverride] = useState(null); // null = auto
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  const home = byName(homeName);
  const away = byName(awayName);
  const autoHost = HOSTS.has(homeName);
  const homeIsHost = hostOverride === null ? autoHost : hostOverride;
  const sameTeam = homeName === awayName;

  function run() {
    if (sameTeam) return;
    setBusy(true);
    // Defer so the "Simulating…" state can paint before the loop runs.
    setTimeout(() => {
      const stats = simulateFixture(home, away, Number(runs) || 10000, {
        seed: seed === "" ? null : seed,
        homeIsHost,
      });
      setResult({ ...stats, homeIsHost });
      setBusy(false);
    }, 10);
  }

  function swap() {
    setHomeName(awayName);
    setAwayName(homeName);
    setHostOverride(null);
  }

  const ratingGap = useMemo(
    () => Math.round(home.rating - away.rating),
    [home, away]
  );

  return (
    <div className="app">
      <header>
        <h1>⚽ World Cup Match Simulator</h1>
        <p className="subtitle">
          Ratings-based Poisson model (Dyte &amp; Clarke style) — runs in your
          browser
        </p>
      </header>

      <section className="panel controls">
        <div className="matchup">
          <TeamSelect label="Home / first team" value={homeName} onChange={setHomeName} />
          <button className="swap" onClick={swap} title="Swap teams">
            ⇄
          </button>
          <TeamSelect label="Away / second team" value={awayName} onChange={setAwayName} />
        </div>

        <div className="options">
          <label className="field small">
            <span className="field-label">Simulations</span>
            <input
              type="number"
              min="100"
              step="1000"
              value={runs}
              onChange={(e) => setRuns(e.target.value)}
            />
          </label>
          <label className="field small">
            <span className="field-label">Seed (optional)</span>
            <input
              type="number"
              placeholder="random"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
            />
          </label>
          <label className="field small checkbox">
            <span className="field-label">Host advantage (home)</span>
            <input
              type="checkbox"
              checked={homeIsHost}
              onChange={(e) => setHostOverride(e.target.checked)}
            />
            <span className="hint">
              {hostOverride === null
                ? autoHost
                  ? "auto: on (co-host)"
                  : "auto: off"
                : "manual"}
            </span>
          </label>
        </div>

        <div className="rating-gap">
          Rating gap: <strong>{ratingGap >= 0 ? "+" : ""}{ratingGap}</strong>{" "}
          in favour of {ratingGap >= 0 ? home.name : away.name}
        </div>

        <button className="run" onClick={run} disabled={busy || sameTeam}>
          {busy ? "Simulating…" : `Simulate ${Number(runs).toLocaleString()} matches`}
        </button>
        {sameTeam && <p className="error">Pick two different teams.</p>}
      </section>

      {result && (
        <section className="panel results">
          <h2>
            {result.home} vs {result.away}
            <span className="meta">
              {result.n.toLocaleString()} simulations
              {result.homeIsHost ? ` · ${result.home} at home` : " · neutral venue"}
            </span>
          </h2>

          <OutcomeBar
            label={`${result.home} win`}
            prob={result.pHome}
            count={result.homeWins}
            color="#2563eb"
          />
          <OutcomeBar label="Draw" prob={result.pDraw} count={result.draws} color="#9ca3af" />
          <OutcomeBar
            label={`${result.away} win`}
            prob={result.pAway}
            count={result.awayWins}
            color="#dc2626"
          />

          <div className="goals">
            Expected goals: <strong>{result.home} {result.avgHomeGoals.toFixed(2)}</strong>{" "}
            — <strong>{result.avgAwayGoals.toFixed(2)} {result.away}</strong>
          </div>

          <h3>Most likely scorelines</h3>
          <ul className="scorelines">
            {result.topScorelines.map((s) => {
              const [hg, ag] = s.score.split("-");
              return (
                <li key={s.score}>
                  <span className="score">
                    {result.home} {hg}–{ag} {result.away}
                  </span>
                  <span className="score-prob">{pct(s.prob)}</span>
                </li>
              );
            })}
          </ul>
        </section>
      )}

      <footer>
        <p>
          Goals are modelled as independent Poisson variables; λ depends on the
          FIFA-rating gap plus a host boost. ★ marks 2026 co-hosts (USA, Canada,
          Mexico).
        </p>
      </footer>
    </div>
  );
}
