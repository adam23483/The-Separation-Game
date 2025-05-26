import json
import pprint

# turns raw fbref export into structured json
def process_fbref_data(input_path, output_path):
    # track unique items for output
    players, teams, seasons, leagues, postions, player_team_seasons = [], [], [], [], [], []
    
    # lookup tables to prevent duplicates
    player_ext_to_id = {}
    team_ext_to_id = {}
    season_name_to_id = {}
    postion_name_to_id = {}
    
    # keep track of ids
    id_counters = {
        "players": 1,
        "teams": 1,
        "seasons": 1,
        "leagues": 1,
        "postions": 1,
        "player_team_season": 1
    }

    # read fbref export
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # go through each player entry
    for player_ext_id, player_data in raw_data.items():
        player_info = player_data["player_info"]
        name = player_info["name"]
        nation = player_info["nation"]
        age = player_info["age"]
        positions = player_info["postions"]  # typo is in original data, change on next webscrape run        

        # check if positions are already added — create if new
        position_ids = []
        for pos in positions:
            if pos not in postion_name_to_id:
                postion_name_to_id[pos] = id_counters["postions"]
                postions.append({
                    "postion_id": id_counters["postions"],
                    "postion": pos
                })
                id_counters["postions"] += 1
            position_ids.append(postion_name_to_id[pos])

        # add player with first position only
        player_id = id_counters["players"]
        players.append({
            "player_id": player_id,
            "player_ext_id": player_ext_id,
            "player_name": name,
            "player_nation": nation,
            "player_age": age,
            "player_postions": position_ids[0]
        })
        player_ext_to_id[player_ext_id] = player_id
        id_counters["players"] += 1

        # loop through each season they played
        for season, season_data in player_data["seasons_played"].items():
            # check if season already exists
            if season not in season_name_to_id:
                season_id = id_counters["seasons"]
                seasons.append({"season_id": season_id, "season": season})
                season_name_to_id[season] = season_id
                id_counters["seasons"] += 1
            else:
                season_id = season_name_to_id[season]

            # loop through teams they played for that season
            for team_name, team_ext_id in season_data["teams"].items():
                # check if team exists — add if not
                if team_ext_id not in team_ext_to_id:
                    team_id = id_counters["teams"]
                    teams.append({
                        "team_id": team_id,
                        "team_ext_id": team_ext_id,
                        "team_name": team_name,
                        "league_id": None  # placeholder
                    })
                    team_ext_to_id[team_ext_id] = team_id
                    id_counters["teams"] += 1
                else:
                    team_id = team_ext_to_id[team_ext_id]

                # create a player_team_season link
                pts_id = id_counters["player_team_season"]
                player_team_seasons.append({
                    "player_team_season_id": pts_id,
                    "player_id": player_id,
                    "season_id": season_id,
                    "team_id": team_id
                })
                id_counters["player_team_season"] += 1

    # final result to export
    output_data = {
        "players": players,
        "teams": teams,
        "seasons": seasons,
        "postions": postions,
        "player_team_seasons": player_team_seasons
    }

    # save output json file
    with open(output_path, "w", encoding="utf-8") as out_file:
        json.dump(output_data, out_file, indent=2)

    # optional preview to terminal
    pprint.pprint(output_data)
