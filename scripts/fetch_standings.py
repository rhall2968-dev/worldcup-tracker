import os
import json
import requests
from datetime import datetime, timezone

API_KEY = os.environ.get("FOOTBALL_DATA_API_KEY", "")
BASE_URL = "https://api.football-data.org/v4"
COMPETITION = "WC"  # football-data.org competition code for FIFA World Cup

DRAFTERS = {
    "Dogg": ["France", "Morocco", "USA", "Colombia", "Ecuador"],
    "Beet": ["Spain", "Croatia", "Belgium", "Uruguay", "Ivory Coast"],
    "Joven": ["Argentina", "Netherlands", "Japan", "Turkey", "Austria"],
    "Kid":  ["England", "Brazil", "Mexico", "Senegal", "Korea"],
    "Dike": ["Portugal", "Germany", "Norway", "Switzerland", "Sweden"],
}

# football-data.org team names → our draft names
API_NAME_MAP = {
    "Korea Republic":    "Korea",
    "Republic of Korea": "Korea",
    "Côte d'Ivoire":     "Ivory Coast",
    "United States":     "USA",
    "Türkiye":           "Turkey",
}

POINTS = {"WIN": 3, "OTW": 2, "TIE": 1, "OTL": 1, "LOSS": 0}


def normalize(name):
    return API_NAME_MAP.get(name, name)


def is_overtime(match):
    et  = match["score"].get("extraTime") or {}
    pen = match["score"].get("penalties") or {}
    return et.get("home") is not None or pen.get("home") is not None


def result_for(match, team):
    home   = normalize(match["homeTeam"]["name"])
    away   = normalize(match["awayTeam"]["name"])
    winner = match["score"]["winner"]  # HOME_TEAM | AWAY_TEAM | DRAW

    if winner == "DRAW":
        return "TIE"

    is_home = team == home
    won = (winner == "HOME_TEAM" and is_home) or (winner == "AWAY_TEAM" and not is_home)

    if won:
        return "OTW" if is_overtime(match) else "WIN"
    else:
        return "OTL" if is_overtime(match) else "LOSS"


def empty_record():
    return {"W": 0, "L": 0, "T": 0, "OTW": 0, "OTL": 0, "pts": 0}


def main():
    team_drafter = {team: d for d, teams in DRAFTERS.items() for team in teams}
    records = {d: {t: empty_record() for t in teams} for d, teams in DRAFTERS.items()}

    if not API_KEY:
        print("Warning: FOOTBALL_DATA_API_KEY not set — writing zero standings.")
    else:
        try:
            headers = {"X-Auth-Token": API_KEY}
            resp = requests.get(
                f"{BASE_URL}/competitions/{COMPETITION}/matches",
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            matches = resp.json().get("matches", [])
            print(f"Fetched {len(matches)} matches.")

            for match in matches:
                if match.get("status") != "FINISHED":
                    continue

                home = normalize(match["homeTeam"]["name"])
                away = normalize(match["awayTeam"]["name"])

                for team in (home, away):
                    if team not in team_drafter:
                        continue
                    drafter = team_drafter[team]
                    result  = result_for(match, team)
                    rec     = records[drafter][team]

                    if result == "WIN":    rec["W"]   += 1
                    elif result == "LOSS": rec["L"]   += 1
                    elif result == "TIE":  rec["T"]   += 1
                    elif result == "OTW":  rec["OTW"] += 1
                    elif result == "OTL":  rec["OTL"] += 1

                    rec["pts"] += POINTS[result]

        except Exception as e:
            print(f"Error fetching from API: {e}")
            print("Writing standings with current data (zeros if first run).")

    output = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "drafters": {
            d: {
                "total_points": sum(t["pts"] for t in teams.values()),
                "teams": teams,
            }
            for d, teams in records.items()
        },
    }

    os.makedirs("data", exist_ok=True)
    with open("data/standings.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Standings written at {output['last_updated']}")


if __name__ == "__main__":
    main()
