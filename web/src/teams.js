// JavaScript port of teams.py — kept in sync with the Python data.
// Ratings are approximate FIFA points (modern scale).

export const TEAMS = [
  { name: "Argentina", rating: 1886, group: "A" },
  { name: "Mexico", rating: 1687.48, group: "A" }, // FIFA points, 11 Jun 2026 (rank 14)
  { name: "Poland", rating: 1546, group: "A" },
  { name: "Saudi Arabia", rating: 1419, group: "A" },

  { name: "France", rating: 1859, group: "B" },
  { name: "Senegal", rating: 1630, group: "B" },
  { name: "Japan", rating: 1652, group: "B" },
  { name: "Canada", rating: 1531, group: "B" },

  { name: "Spain", rating: 1854, group: "C" },
  { name: "Croatia", rating: 1716, group: "C" },
  { name: "Morocco", rating: 1694, group: "C" },
  { name: "South Korea", rating: 1575, group: "C" },

  { name: "England", rating: 1840.46, group: "D" }, // FIFA points, 11 Jun 2026 (rank 4)
  { name: "Netherlands", rating: 1745, group: "D" },
  { name: "USA", rating: 1671.23, group: "D" }, // FIFA points, 11 Jun 2026 (rank 17)
  { name: "Australia", rating: 1488, group: "D" },

  { name: "Brazil", rating: 1776, group: "E" },
  { name: "Portugal", rating: 1761, group: "E" },
  { name: "Switzerland", rating: 1650, group: "E" }, // FIFA points, 11 Jun 2026 (rank 19)
  { name: "Ghana", rating: 1450, group: "E" },

  { name: "Belgium", rating: 1737, group: "F" },
  { name: "Germany", rating: 1717, group: "F" },
  { name: "Ecuador", rating: 1598.52, group: "F" }, // FIFA points, 11 Jun 2026 (rank 23)
  { name: "Qatar", rating: 1400, group: "F" },

  { name: "Italy", rating: 1718, group: "G" },
  { name: "Uruguay", rating: 1639, group: "G" },
  { name: "Colombia", rating: 1698.35, group: "G" }, // FIFA points, 11 Jun 2026 (rank 13)
  { name: "Nigeria", rating: 1503, group: "G" },

  { name: "Bosnia and Herzegovina", rating: 1387.22, group: "B" }, // FIFA points, 11 Jun 2026 (rank 64)

  { name: "Denmark", rating: 1666, group: "H" },
  { name: "Mexico B", rating: 1600, group: "H" },
  { name: "Serbia", rating: 1549, group: "H" },
  { name: "Iran", rating: 1500, group: "H" },
];

// The 2026 World Cup is co-hosted by the USA, Canada and Mexico.
export const HOSTS = new Set(["USA", "Canada", "Mexico"]);

export function byName(name) {
  const t = TEAMS.find((x) => x.name === name);
  if (!t) throw new Error(`Unknown team: ${name}`);
  return t;
}
