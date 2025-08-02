import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
import pprint
import subprocess

# GET PLAYER GLOBAL ID
def extract_player_id(player_url):
    match = re.search(r"/players/([a-z0-9]{8})/", player_url)
    return match.group(1) if match else None

# GET TEAM GLOBAL ID
def extract_team_id(team_url):
    match = re.search(r"/squads/([a-z0-9]{8})/", team_url)
    return match.group(1) if match else None

# GET PLAYER NATION
def extract_player_nation(nation_url):
    nation = nation_url.split("/")[-1].replace("-Football", "")
    return nation if nation else None

# MAP POSITION NAMES
def get_full_position(short_position):
    position_mapping = {
        "GK": "Goalkeeper", "DF": "Defender", "MF": "Midfielder", "FW": "Forward",
        "FB": "FullBack", "LB": "Left Back", "RB": "Right Back", "CB": "Center Back",
        "DM": "Defensive Midfielder", "CM": "Central Midfielder", "LM": "Left Midfielder",
        "RM": "Right Midfielder", "WM": "Wide Midfielder", "LW": "Left Winger",
        "RW": "Right Winger", "AM": "Attacking Midfielder"
    }
    return [position_mapping.get(p.strip(), p.strip()) for p in short_position.split(",")]

# EXTRACT LEAGUE ID, SEASON, AND LEAGUE NAME
def extract_league_id_season_and_league(url):
    league_id_match = re.search(r'/comps/(\d+)', url)
    league_id = league_id_match.group(1) if league_id_match else "Unknown"
    last_part = url.rstrip('/').split('/')[-1]
    match = re.match(r"(\d{4}-\d{4})-(.+?)-Stats", last_part)
    if match:
        season = match.group(1)
        league = match.group(2).replace('-', ' ')
    else:
        season = "2024-2025"
        league_match = re.match(r"(.+?)-Stats", last_part)
        league = league_match.group(1).replace('-', ' ') if league_match else "Unknown"
    return {"league_id": league_id, "season": season, "league": league}

# BUILD SEASON URLS
def get_stat_urls(base_urls, start_year, end_year, last_year):
    urls = []
    for base in base_urls:
        start_year_loop = start_year 
        end_year_loop = end_year
        urls.append(base)

        match = re.search(r"/(stats|playingtime)/", base)
        if not match:
            continue
        section = match.group(1)

        # Extract league name from the last part of the URL
        base_parts = base.rstrip('/').split('/')
        last_part = base_parts[-1]  # e.g., "La-Liga-Stats"
        league_part = last_part.replace("-Stats", "")

        while start_year_loop > last_year:
            start_year_loop -= 1
            end_year_loop -= 1
            # Construct the historical URL
            historical = f"{'/'.join(base_parts[:-2])}/{start_year_loop}-{end_year_loop}/{section}/{start_year_loop}-{end_year_loop}-{league_part}-Stats"
            urls.append(historical)
            print(historical)
    return urls

# SCRAPE DATA
def scrape_players_data(league_urls):
    players_dict = {}
    headers = {'user-agent': 'Mozilla/5.0'}

    for url in league_urls:
        time.sleep(random.randint(5, 10))
        print(f"\n[INFO] Scraping: {url}")
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=15)
                if not response.ok:
                    raise Exception(f"Bad status code {response.status_code}")
                break
            except Exception as e:
                print(f"[WARN] Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == 2:
                    print(f"[ERROR] Skipping {url} after 3 attempts")
                    continue
                time.sleep(3)

        html = response.text.replace("<!--", "").replace("-->", "")
        soup = BeautifulSoup(html, "html5lib")
        tables = soup.find_all("table")

        league_season = extract_league_id_season_and_league(url)
        season = league_season["season"]
        league_id = league_season["league_id"]
        league_name = league_season["league"]

        for table in tables:
            caption = table.find("caption")
            if not caption:
                continue

            caption_text = caption.get_text().lower()
            if not any(key in caption_text for key in ["player", "stats", "playing time", "standard"]):
                continue

            stats_rows = table.find_all("tr")
            for row in stats_rows:
                stats = row.find_all("td")
                if not stats:
                    continue

                player_id = name = nation = age = position = team_name = team_id = None

                for stat in stats:
                    stat_type = stat.get("data-stat")
                    if stat_type == "player":
                        name = stat.get_text().strip()
                        link = stat.find("a")
                        if link:
                            player_id = extract_player_id(link["href"])
                    elif stat_type == "team":
                        team_name = stat.get_text().strip()
                        link = stat.find("a")
                        if link:
                            team_id = extract_team_id(link["href"])
                    elif stat_type == "nationality":
                        link = stat.find("a")
                        if link:
                            nation = extract_player_nation(link["href"])
                    elif stat_type == "age":
                        age = stat.get_text()[:2]
                        age = int(age) if age.isdigit() else None
                    elif stat_type == "position":
                        position = get_full_position(stat.get_text())

                if not player_id:
                    continue

                # Create player if not exists
                if player_id not in players_dict:
                    players_dict[player_id] = {
                        "player_info": {
                            "name": name, "nation": nation, "age": age, "postions": position
                        },
                        "seasons_played": {}
                    }
                else:
                    # Merge missing info
                    pinfo = players_dict[player_id]["player_info"]
                    if not pinfo["name"] and name:
                        pinfo["name"] = name
                    if not pinfo["nation"] and nation:
                        pinfo["nation"] = nation
                    if not pinfo["age"] and age:
                        pinfo["age"] = age
                    if not pinfo["postions"] and position:
                        pinfo["postions"] = position

                # Add team/season info
                if season not in players_dict[player_id]["seasons_played"]:
                    players_dict[player_id]["seasons_played"][season] = {"teams": {}}
                if team_name and team_id:
                    players_dict[player_id]["seasons_played"][season]["teams"][team_name] = {
                        "team_id": team_id,
                        "league_id": league_id,
                        "league_name": league_name
                    }

        print(f"[INFO] Players so far: {len(players_dict)}")

    return players_dict


# PROCESS RAW TO STRUCTURED DATA
def process_fbref_data(raw_data, output_path):
    players, teams, seasons, positions, player_team_seasons, leagues = [], [], [], [], [], []
    player_ext_to_id, team_ext_to_id = {}, {}
    season_name_to_id, position_name_to_id, league_name_to_id = {}, {}, {}
    ids = {"players":1, "teams":1, "seasons":1, "positions":1, "player_team_season":1, "leagues":1}

    for player_ext_id, pdata in raw_data.items():
        pinfo = pdata["player_info"]
        name, nation, age, pos_list = pinfo["name"], pinfo["nation"], pinfo["age"], pinfo["postions"]

        pos_ids = []
        for pos in pos_list:
            if pos not in position_name_to_id:
                position_name_to_id[pos] = ids["positions"]
                positions.append({"position_id": ids["positions"], "position": pos})
                ids["positions"] += 1
            pos_ids.append(position_name_to_id[pos])

        pid = ids["players"]
        players.append({"player_id": pid, "player_ext_id": player_ext_id, "player_name": name,
                        "player_nation": nation, "player_age": age, "player_positions": pos_ids[0]})
        player_ext_to_id[player_ext_id] = pid
        ids["players"] += 1

        for season, sdata in pdata["seasons_played"].items():
            if season not in season_name_to_id:
                season_name_to_id[season] = ids["seasons"]
                seasons.append({"season_id": ids["seasons"], "season": season})
                ids["seasons"] += 1
            sid = season_name_to_id[season]

            for team_name, team_info in sdata["teams"].items():
                team_ext_id = team_info["team_id"]
                league_id = team_info["league_id"]
                league_name = team_info["league_name"]

                if league_id not in league_name_to_id:
                    league_name_to_id[league_id] = ids["leagues"]
                    leagues.append({"league_id": league_id, "league_name": league_name})
                    ids["leagues"] += 1

                if team_ext_id not in team_ext_to_id:
                    team_ext_to_id[team_ext_id] = ids["teams"]
                    teams.append({"team_id": ids["teams"], "team_ext_id": team_ext_id,
                                  "team_name": team_name, "league_id": league_id})
                    ids["teams"] += 1
                tid = team_ext_to_id[team_ext_id]

                pts_id = ids["player_team_season"]
                player_team_seasons.append({"player_team_season_id": pts_id, "player_id": pid,
                                            "season_id": sid, "team_id": tid})
                ids["player_team_season"] += 1

    structured = {
        "players": players,
        "teams": teams,
        "seasons": seasons,
        "positions": positions,
        "leagues": leagues,
        "player_team_seasons": player_team_seasons
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2)

# MAIN EXECUTION
base_urls = [
    "https://fbref.com/en/comps/9/playingtime/Premier-League-Stats",
    "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
    "https://fbref.com/en/comps/12/playingtime/La-Liga-Stats",
    "https://fbref.com/en/comps/12/stats/La-Liga-Stats",
    "https://fbref.com/en/comps/11/playingtime/Serie-A-Stats",
    "https://fbref.com/en/comps/11/stats/Serie-A-Stats",
    "https://fbref.com/en/comps/20/playingtime/Bundesliga-Stats",
    "https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
    "https://fbref.com/en/comps/13/playingtime/Ligue-1-Stats",
    "https://fbref.com/en/comps/13/stats/Ligue-1-Stats"
]

start_year = 2024
end_year = 2025
last_year = 1988

urls = get_stat_urls(base_urls, start_year, end_year, last_year)
raw_data = scrape_players_data(urls)
with open(r"C:\Users\zack2\OneDrive\Documents\GitHub\The-Separation-Game\json_data\fbref_players.json", "w") as f:
    json.dump(raw_data, f, indent=2)

process_fbref_data(raw_data, r"C:\Users\zack2\OneDrive\Documents\GitHub\The-Separation-Game\json_data\processed_fbref_data.json")

subprocess.run(["python", r"C:\Users\zack2\OneDrive\Documents\GitHub\The-Separation-Game\python_code\sql_uplaod.py"])
