const TOURNAMENT_START = new Date('2026-06-11');
const RANKS = ['🥇', '🥈', '🥉'];

async function loadStandings() {
  const resp = await fetch('./data/standings.json');
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const data = await resp.json();

  updateHeader(data.last_updated);
  maybeShowPreTournamentBanner(data);

  const sorted = Object.entries(data.drafters)
    .sort(([, a], [, b]) => b.total_points - a.total_points);

  renderLeaderboard(sorted);
  renderCards(sorted);
}

function updateHeader(ts) {
  const d = new Date(ts);
  const opts = { month: 'long', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' };
  document.getElementById('last-updated').textContent =
    `Last updated: ${d.toLocaleDateString('en-US', opts)}`;
}

function maybeShowPreTournamentBanner(data) {
  const allZero = Object.values(data.drafters).every(d => d.total_points === 0);
  if (!allZero) return;

  const now = new Date();
  if (now < TOURNAMENT_START) {
    const banner = document.createElement('div');
    banner.className = 'pre-tournament';
    banner.textContent = '🗓 Tournament begins June 11, 2026 — standings will update nightly once matches start.';
    document.querySelector('main').prepend(banner);
  }
}

function renderLeaderboard(sorted) {
  const tbody = document.getElementById('standings-body');
  sorted.forEach(([name, drafter], i) => {
    const totals = sumTeams(drafter.teams);
    const possiblePts = calcPossiblePoints(totals);
    const record = `${totals.W}-${totals.L}-${totals.T}`;
    const rank = i + 1;
    const medal = RANKS[i] ?? rank;
    const tr = document.createElement('tr');
    if (rank <= 3) tr.className = `rank-${rank}`;
    tr.innerHTML = `
      <td>${medal}</td>
      <td class="drafter-name">${name}</td>
      <td class="total-pts">${drafter.total_points}</td>
      <td>${record}</td>
      <td>${possiblePts}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderCards(sorted) {
  const container = document.getElementById('drafter-cards');
  sorted.forEach(([name, drafter], i) => {
    const rank = RANKS[i] ?? `#${i + 1}`;
    const teams = Object.entries(drafter.teams)
      .sort(([, a], [, b]) => b.pts - a.pts);

    const rows = teams.map(([team, r]) => `
      <tr>
        <td class="team-name">${team}</td>
        <td class="cell-w">${r.W}</td>
        <td class="cell-otw">${r.OTW}</td>
        <td class="cell-t">${r.T}</td>
        <td class="cell-otl">${r.OTL}</td>
        <td class="cell-l">${r.L}</td>
        <td class="team-pts">${r.pts}</td>
      </tr>
    `).join('');

    const card = document.createElement('div');
    card.className = 'drafter-card';
    card.innerHTML = `
      <div class="card-header">
        <span class="card-rank">${rank}</span>
        <h3>${name}</h3>
        <span class="card-pts">${drafter.total_points} pts</span>
      </div>
      <table class="team-table">
        <thead>
          <tr>
            <th class="left">Team</th>
            <th title="Wins">W</th>
            <th title="Overtime Wins">OTW</th>
            <th title="Ties">T</th>
            <th title="Overtime Losses">OTL</th>
            <th title="Losses">L</th>
            <th title="Points">Pts</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    `;
    container.appendChild(card);
  });
}

function sumTeams(teams) {
  return Object.values(teams).reduce(
    (acc, t) => ({ W: acc.W + t.W, OTW: acc.OTW + t.OTW, T: acc.T + t.T, OTL: acc.OTL + t.OTL, L: acc.L + t.L }),
    { W: 0, OTW: 0, T: 0, OTL: 0, L: 0 }
  );
}

function calcPossiblePoints(totals) {
  const gamesPlayed = totals.W + totals.OTW + totals.T + totals.OTL + totals.L;
  return gamesPlayed * 3;
}

loadStandings().catch(err => {
  document.getElementById('last-updated').textContent = 'Could not load standings.';
  console.error(err);
});
