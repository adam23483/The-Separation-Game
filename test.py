import json

# Initialize sets and dicts to track unique items
players, teams, seasons, leagues, postions, player_team_seasons = [], [], [], [], [], []
postion_lookup, league_lookup = {}, {}

# Auto-increment IDs
id_counters = {
    "players": 1,
    "teams": 1,
    "seasons": 1,
    "leagues": 1,
    "postions": 1,
    "player_team_season": 1
}

# Maps for de-duplication
player_ext_to_id = {}
team_ext_to_id = {}
season_name_to_id = {}
postion_name_to_id = {}
league_name_to_id = {}

# Sample input data — replace this with actual file load~
with open(r"C:\Users\zack2\OneDrive\Documents\GitHub\The-Separation-Game\fbref_players.txt", "r", encoding="utf-8") as f:
    raw_data = json.load(f)  # assuming it's stored as valid JSON

for player_ext_id, player_data in raw_data.items():
    player_info = player_data["player_info"]
    name = player_info["name"]
    nation = player_info["nation"]
    age = player_info["age"]
    positions = player_info["postions"]  # typo in original key; keep consistent

    # Add player positions
    position_ids = []
    for pos in positions:
        if pos not in postion_name_to_id:
            postion_name_to_id[pos] = id_counters["postions"]
            postions.append({
                "postion_id": id_counters["postions"],
                "postion": pos
            })
            id_counters["postions"] += 1
        position_ids.append(postion_name_to_id[pos])  # store for player row

    # Add player
    player_id = id_counters["players"]
    players.append({
        "player_id": player_id,
        "player_ext_id": player_ext_id,
        "player_name": name,
        "player_nation": nation,
        "player_age": age,
        "player_postions": position_ids[0]  # Store first position (normalize separately if many-to-many)
    })
    player_ext_to_id[player_ext_id] = player_id
    id_counters["players"] += 1

    # Seasons and teams
    for season, season_data in player_data["seasons_played"].items():
        # Add season
        if season not in season_name_to_id:
            season_id = id_counters["seasons"]
            seasons.append({"season_id": season_id, "season": season})
            season_name_to_id[season] = season_id
            id_counters["seasons"] += 1
        else:
            season_id = season_name_to_id[season]

        for team_name, team_ext_id in season_data["teams"].items():
            # Add team
            if team_ext_id not in team_ext_to_id:
                team_id = id_counters["teams"]
                teams.append({
                    "team_id": team_id,
                    "team_ext_id": team_ext_id,
                    "team_name": team_name,
                    "league_id": None  # You can fill this later if league info is known
                })
                team_ext_to_id[team_ext_id] = team_id
                id_counters["teams"] += 1
            else:
                team_id = team_ext_to_id[team_ext_id]

            # Add player_team_season entry
            pts_id = id_counters["player_team_season"]
            player_team_seasons.append({
                "player_team_season_id": pts_id,
                "player_id": player_id,
                "season_id": season_id,
                "team_id": team_id
            })
            id_counters["player_team_season"] += 1

# Example output display (or write to file/database)
import pprint
pprint.pprint({
    "players": players,
    "teams": teams,
    "seasons": seasons,
    "postions": postions,
    "player_team_seasons": player_team_seasons
})
