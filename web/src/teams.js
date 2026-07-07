// JavaScript port of teams.py — kept in sync with the Python data.
//
// rating = official FIFA points, 11 June 2026 update (verified for all
// Round-of-16 teams; approximate placeholders for the rest).
// live   = unofficial live FIFA points, early July 2026 (group stage +
// Round of 32 reflected), null where no sourced figure exists.

export const TEAMS = [
  { name: "Argentina", rating: 1877.27, group: "A", live: 1913.71 },
  { name: "Mexico", rating: 1687.48, group: "A", live: 1754.3 },
  { name: "France", rating: 1870.7, group: "B", live: 1916.24 },
  { name: "Canada", rating: 1559.48, group: "B", live: 1571.34 },
  { name: "Spain", rating: 1874.71, group: "C", live: 1892.28 },
  { name: "Morocco", rating: 1756.94, group: "C", live: 1788.86 },
  { name: "England", rating: 1840.46, group: "D", live: 1850.97 },
  { name: "USA", rating: 1671.23, group: "D", live: 1690.33 },
  { name: "Brazil", rating: 1765.34, group: "E", live: 1804.92 },
  { name: "Portugal", rating: 1767.85, group: "E", live: 1787.85 },
  // Belgium official total unpublished; earliest in-tournament live figure
  // (1733.93) used as the official-baseline proxy.
  { name: "Belgium", rating: 1733.93, group: "F", live: 1756.51 },
  { name: "Ecuador", rating: 1598.52, group: "F", live: null },
  { name: "Colombia", rating: 1698.35, group: "G", live: 1739.89 },
  { name: "Switzerland", rating: 1650.0, group: "G", live: 1696.3 },
  { name: "Norway", rating: 1557.44, group: "H", live: 1617.67 },
  { name: "Paraguay", rating: 1505.35, group: "H", live: 1542.48 },
  { name: "Egypt", rating: 1562.37, group: "I", live: 1597.04 },
  { name: "Bosnia and Herzegovina", rating: 1387.22, group: "I", live: null },

  // Placeholders (unverified)
  { name: "Poland", rating: 1546, group: "J", live: null },
  { name: "Saudi Arabia", rating: 1419, group: "J", live: null },
  { name: "Senegal", rating: 1630, group: "J", live: null },
  { name: "Japan", rating: 1652, group: "J", live: null },
  { name: "Croatia", rating: 1716, group: "K", live: null },
  { name: "South Korea", rating: 1575, group: "K", live: null },
  { name: "Netherlands", rating: 1745, group: "K", live: null },
  { name: "Australia", rating: 1488, group: "K", live: null },
  { name: "Ghana", rating: 1450, group: "L", live: null },
  { name: "Germany", rating: 1717, group: "L", live: null },
  { name: "Qatar", rating: 1400, group: "L", live: null },
  { name: "Italy", rating: 1718, group: "L", live: null },
  { name: "Uruguay", rating: 1639, group: "M", live: null },
  { name: "Nigeria", rating: 1503, group: "M", live: null },
  { name: "Denmark", rating: 1666, group: "M", live: null },
  { name: "Serbia", rating: 1549, group: "M", live: null },
  { name: "Iran", rating: 1500, group: "M", live: null },
];

// The 2026 World Cup is co-hosted by the USA, Canada and Mexico. Host
// advantage only applies when the co-host actually plays in its own country.
export const HOSTS = new Set(["USA", "Canada", "Mexico"]);

export function byName(name) {
  const t = TEAMS.find((x) => x.name === name);
  if (!t) throw new Error(`Unknown team: ${name}`);
  return t;
}
