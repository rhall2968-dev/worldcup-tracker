# ⚽ World Cup 2026 Draft Tracker

Live standings for a 5-person fantasy draft pool following the **2026 FIFA World Cup** (June 11 – July 19, 2026).

🌐 **[View the live site](https://rhall2968-dev.github.io/worldcup-tracker/)**

---

## Draft Picks

| | Dogg | Reet | Joven | Kid | Dike |
|--|------|------|-------|-----|------|
| 1 | France | Spain | Argentina | England | Portugal |
| 2 | Morocco | Croatia | Netherlands | Brazil | Germany |
| 3 | USA | Belgium | Japan | Mexico | Norway |
| 4 | Colombia | Uruguay | Turkey | Senegal | Switzerland |
| 5 | Ecuador | Ivory Coast | Austria | Korea | Sweden |

---

## Scoring

| Result | Points |
|--------|--------|
| Win | 3 |
| Overtime Win (ET or Penalties) | 2 |
| Tie | 1 |
| Overtime Loss (ET or Penalties) | 1 |
| Loss | 0 |

---

## How It Works

- **Site:** Static HTML/CSS/JS hosted on [GitHub Pages](https://pages.github.com/)
- **Data:** Match results fetched from [worldcup26.ir](https://worldcup26.ir) — free, no API key required
- **Updates:** GitHub Actions runs every night at 4am Eastern, fetches all finished matches, recalculates standings, and commits `data/standings.json`
- **Manual trigger:** Go to **Actions → Update World Cup Standings → Run workflow** to pull the latest results on demand

---

## Project Structure

```
worldcup-tracker/
├── index.html               # Main site
├── style.css                # Styles
├── script.js                # Frontend — reads standings.json and renders the page
├── data/
│   └── standings.json       # Auto-updated nightly by GitHub Actions
├── scripts/
│   └── fetch_standings.py   # Fetches match results and writes standings.json
└── .github/
    └── workflows/
        └── update-standings.yml  # Nightly cron job
```

---

## Tournament

- **Opening match:** June 11, 2026 — Mexico City
- **Final:** July 19, 2026 — New Jersey
- **Format:** 48 teams, 12 groups, 104 total matches
