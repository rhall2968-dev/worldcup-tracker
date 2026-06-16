import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timezone
import os

API_URL = "https://worldcup26.ir/get/games"

# Disable SSL verification for the Iranian API
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

DRAFTERS = {
    "Dogg": ["France", "Morocco", "USA", "Colombia", "Ecuador"],
    "Reet": ["Spain", "Croatia", "Belgium", "Uruguay", "Ivory Coast"],
    "Joven": ["Argentina", "Netherlands", "Japan", "Turkey", "Austria"],
    "Kid":  ["England", "Brazil", "Mexico", "Senegal", "Korea"],
    "Dike": ["Portugal", "Germany", "Norway", "Switzerland", "Sweden"],
}

# worldcup26.ir name → our draft name
API_NAME_MAP = {
    "South Korea":   "Korea",
    "United States": "USA",
}

POINTS = {"WIN": 3, "OTW": 2, "TIE": 1, "OTL": 1, "LOSS": 0}


def normalize(name):
    return API_NAME_MAP.get(name, name)


def is_overtime(match):
    elapsed = (match.get("time_elapsed") or "").upper()
    return "AET" in elapsed or "PEN" in elapsed


def result_for(match, team):
    home  = normalize(match["home_team_name_en"])
    away  = normalize(match["away_team_name_en"])
    h_score = int(match.get("home_score") or 0)
    a_score = int(match.get("away_score") or 0)

    is_home = team == home
    ot      = is_overtime(match)

    if h_score == a_score:
        # Draws only happen in group stage
        return "TIE"

    won = (h_score > a_score and is_home) or (a_score > h_score and not is_home)

    if won:
        return "OTW" if ot else "WIN"
    else:
        return "OTL" if ot else "LOSS"


def empty_record():
    return {"W": 0, "L": 0, "T": 0, "OTW": 0, "OTL": 0, "pts": 0}


def main():
    team_drafter = {team: d for d, teams in DRAFTERS.items() for team in teams}
    records      = {d: {t: empty_record() for t in teams} for d, teams in DRAFTERS.items()}

    try:
        req = urllib.request.Request(API_URL)
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            data = response.read()
            response_text = data.decode('utf-8')
            # Handle both dict and list responses
            response_data = json.loads(response_text)
            matches = response_data.get('games', []) if isinstance(response_data, dict) else response_data
        print(f"Fetched {len(matches)} matches.")

        for match in matches:
            if str(match.get("finished", "")).upper() != "TRUE":
                continue

            home = normalize(match["home_team_name_en"])
            away = normalize(match["away_team_name_en"])

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
