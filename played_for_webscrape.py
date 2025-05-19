import requests
from bs4 import BeautifulSoup
import mysql.connector
import json
import re
import time 
import random



def get_stat_urls(league_urls, season_start_year, season_end_year, last_season_year):   
    urls_list = []

    for league in league_urls:
        urls_list.append(league)

        # Reset the season years for each league
        start_year = season_start_year
        end_year = season_end_year

        while start_year > last_season_year:
            start_year -= 1
            end_year -= 1
            league_url = league.replace("/stats/", f"/{start_year}-{end_year}/stats/{start_year}-{end_year}-")
            print(league_url)
            urls_list.append(league_url)

    return urls_list

# finds stats table on fbref
def get_stats_table(soup):
    full_table = ""
    for x in soup.select("th"):
        x.decompose()

    # find the table with the player stats 
    for table in get_stats_table:
        table_caption = table.find("caption")
        table_name_text = table_caption.get_text()
        if "Player Standard Stats " in table_name_text:
            full_table = table_caption.parent

    return full_table     

def extract_season_and_league(url):
    # Get the last part of the URL
    last_part = url.rstrip('/').split('/')[-1]

    # Try to extract the season and league
    match = re.match(r"(\d{4}-\d{4})-(.+?)-Stats", last_part)
    if match:
        season = match.group(1)
        league = match.group(2).replace('-', ' ')
    else:
        # If no season is found, assume 2024-2025 and try to extract league name
        season = "2024-2025"
        # Try extracting league from format like "Premier-League-Stats"
        league_match = re.match(r"(.+?)-Stats", last_part)
        if league_match:
            league = league_match.group(1).replace('-', ' ')
        else:
            league = "Unknown"

    return {"season": season, "league": league}

def extract_player_id(player_url):
    match = re.search(r"/players/([a-z0-9]{8})/", player_url)
    return match.group(1) if match else None

def extract_team_id(team_url):
    match = re.search(r"/squads/([a-z0-9]{8})/", team_url)
    return match.group(1) if match else None

def extract_player_nation(nation_url):
    nation = nation_url.split("/")[-1].replace("-Football", "")
    return nation if nation else None

def get_player_ids(player_id, player_dict):
    
    if player_id not in player_dict:
        players_dict[player_id] = {}
        players_dict[player_id]["player_info"] = {
            "name": "",
            "nation": "",
            "age": "",
            "postions": ""
        }
        players_dict[player_id]["seasons_played"] =  {}
        return (player_id, False)  # New player added
    else:
        return (player_id, True) 

def get_player_team_season(players_dict, season, player_id, team_name, team_id):
    if player_id in players_dict:

        if players_dict[player_id]["seasons_played"] == {}:
            players_dict[player_id]["seasons_played"][season] = {"teams":{}}
        
        if season not in players_dict[player_id]["seasons_played"]:
            players_dict[player_id]["seasons_played"][season] = {"teams":{}}

        if team_name not in players_dict[player_id]["seasons_played"][season]["teams"] :
            players_dict[player_id]["seasons_played"][season]["teams"][team_name] = team_id
            return (player_id, True)  # Player already exists, team added

def get_full_position(short_position):
    position_mapping = {
        "GK": "Goalkeeper",
        "DF": "Defender",
        "MF": "Midfielder",
        "FW": "Forward",
        "FB": "FullBack",
        "LB": "Left Back",
        "RB": "Right Back",
        "CB": "Center Back",
        "DM": "Defensive Midfielder",
        "CM": "Central Midfielder",
        "LM": "Left Midfielder",
        "RM": "Right Midfielder",
        "WM": "Wide Midfielder",
        "LW": "Left Winger",
        "RW": "Right Winger",
        "AM": "Attacking Midfielder"
    }

    # Split by comma and strip spaces
    positions = [position.strip() for position in short_position.split(",")]

    # Map each to full name, fallback to the short version if not found
    full_positions = [] 
    for position in positions:
        full_position = position_mapping.get(position, position)
        if full_position not in full_positions:
            full_positions.append(full_position)
    return full_positions

    # If the short position isn't found, just return the original
    return position_mapping.get(short_position, short_position)
    
def get_player_info(players_dict, player_id, player_name, player_nation, player_age, player_position):

    if player_id in players_dict and "player_info" in players_dict[player_id]:
        players_dict[player_id]["player_info"]["name"] = player_name
        players_dict[player_id]["player_info"]["nation"] = player_nation
        players_dict[player_id]["player_info"]["age"] = player_age
        players_dict[player_id]["player_info"]["postions"] = player_position
    else:
        print(f"Player ID {player_id} not found in players dictionary.")

def get_table_data(league_urls, players_dict,season_start_year, season_end_year, last_season_year):

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    for url in league_urls: 
        random_integer = random.randint(1, 5)
        time.sleep(random_integer) # Sleep for a random time between 1 and 5 seconds
        response = requests.get(url,headers=headers)
        if response.ok:
            # .replace() removes player data comment out to see player data
            html_content = response.text.replace("<!--", "").replace("-->", "")
            soup = BeautifulSoup(html_content, "html5lib")
        else:
            print(f"Failed - League: {url}")
            print(response.reason)

        # finds stats table on fbref
        get_stats_table = soup.find_all("table")
        full_table = ""
        for x in soup.select("th"):
            x.decompose()

        # find the table with the player stats 
        for table in get_stats_table:
            table_caption = table.find("caption")
            table_name_text = table_caption.get_text()
            if "Player" in table_name_text:
                full_table = table_caption.parent

        # finds the data-stat ids and create key/value pair for player stats
        stats_table = full_table.find_all("tr")
        if not stats_table:
            print(f"Failed - No stats table found for {url}")
            continue
        
        for rows in stats_table:
            stat_column = rows.find_all("td")
            player_id = ""
            player_name = "" 
            player_nation = ""
            player_age = ""
            player_position = "" 
            team_id = "" 
            team_name = ""
            
            league_season = extract_season_and_league(url)
            league = league_season.get("league")
            season = league_season.get("season")
            season= tuple(map(int, season.split('-')))
        
            for stat in stat_column:
                league = league_season.get("league")
                season = league_season.get("season")
                if not stat.has_attr("data-stat"):
                    continue
                stat_tag = stat["data-stat"]
# GET PLAYER NAME          
                if stat_tag == "player":
                    player_name = stat.get_text() 
                    player_url = stat.find("a")
# GET PLAYER GLOBAL ID
                    if player_url:
                        player_url = player_url["href"]
                        player_id = extract_player_id(player_url)
                    else:
                        player_url = None
                get_player_ids(player_id, players_dict)

# GET PLAYER TEAM

                if stat_tag == "team":
                    team_name = stat.get_text()
                    team_url = stat.find("a")
                    if team_url:
                        team_url = team_url["href"]
                        team_id = extract_team_id(team_url) 
                    else:
                        team_id = None
                    get_player_team_season(players_dict, season, player_id, team_name, team_id)


# GET PLAYER NATION                     
                if stat_tag == "nationality":
                    nation_url = stat.find("a")
                    if nation_url:
                        nation_url= nation_url["href"]
                        player_nation = extract_player_nation(nation_url)  #PLAYER NATION
                    else:   
                        player_nation = None
# GET PLAYER AGE

                if stat_tag == "age":
                    player_age = stat.get_text()
                    player_age = player_age[:2]
                    player_age = int(player_age) if player_age.isdigit() else player_age

                if stat_tag == "position":
                    short_position = stat.get_text()
                    player_position = get_full_position(short_position)
                get_player_info(players_dict, player_id, player_name, player_nation, player_age, player_position)
    
league_urls = [
        "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
        "https://fbref.com/en/comps/12/stats/La-Liga-Stats",
        "https://fbref.com/en/comps/11/stats/Serie-A-Stats",
        "https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
        "https://fbref.com/en/comps/13/stats/Ligue-1-Stats"
]

season_start_year = 2024
season_end_year = 2025
last_season_year = 2000
players_dict = {}

league_urls = get_stat_urls(league_urls, season_start_year, season_end_year, last_season_year)

get_table_data(league_urls, players_dict,season_start_year, season_end_year, last_season_year)

print(f"Total players found: {len(players_dict)}")

json_string = json.dumps(players_dict, indent=4)

output_file =r"C:\Users\zack2\OneDrive\Documents\GitHub\The-Separation-Game\fbref_players.txt"
with open(output_file, "w") as file:
    file.write(json_string)
