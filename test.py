import requests
from bs4 import BeautifulSoup
import mysql.connector
import json
import re


def get_stat_urls(league_urls):   
    urls_list = []

    for league in league_urls:
        season_start_year = 2024
        season_end_year = 2025
        last_season_year = 2010

        urls_list.append(league)
        while season_start_year != last_season_year:
            season_start_year -= 1
            season_end_year -= 1
            league_url = league.replace("/stats/", f"/{season_start_year}-{season_end_year}/stats/{season_start_year}-{season_end_year}-")
            urls_list.append(league_url)
            print(f"Added URL: {league_url}")
    #print(f"Total URLs generated: {len(urls_list)}")
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


# input urls for each league #################################################
league_urls = [
        "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
        #"https://fbref.com/en/comps/12/stats/La-Liga-Stats",
        #"https://fbref.com/en/comps/11/stats/Serie-A-Stats",
        #https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
        #"https://fbref.com/en/comps/13/stats/Ligue-1-Stats"
]


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

def add_player_to_dictionary(players_dict, 
                             player_id, 
                             player_name, 
                             player_nation, 
                             team_id, 
                             team_name,
                             season,
                             player_age
                            ):
    #print(player_id)
    #print(player_name)
    #print(player_nation) 
    #print(team_id)
    #print(team_name)
    #print(season)
    #print(player_age)


    if player_id not in players_dict:
        players_dict[player_id] = {}
        player = players_dict[player_id]
        player["seasons_played"] = {season:{"teams":{team_name:team_id}}}
        player["player_info"] = {
            "name": player_name,
            "nation": player_nation,
            "age": player_age,
            "team_id": team_id, 
            "current_team": team_name,
        }
    elif player_id in players_dict:
        player = players_dict[player_id]
        if season not in player["seasons_played"]:
            player["seasons_played"] = {season:{"teams":{team_name:team_id}}}
        else:
            if team_name not in player["seasons_played"][season]["teams"]:
                player["seasons_played"][season]["teams"][team_name] = team_id                
        player["player_info"] = {
            "team_id": team_id,  # Placeholder for team ID
            "current_team": team_name,  # Placeholder for team name
        } 
    #print(f"Added player: {player_name}, ID: {player_id}, Nation: {player_nation}, Team: {team_name}, Age: {player_age}, Season: {season}")

def get_table_data(league_urls, players_dict):

    url_list = get_stat_urls(league_urls)

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    for url in league_urls: #changeto url list later  
        league_season = extract_season_and_league(url)
        league = league_season.get("league")
        season = league_season.get("season")
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
            team_id = "" 
            team_name = ""
            season = ""
            player_age = ""

            for stat in stat_column:

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
# GET PLAYER NATION                     
                
                elif stat_tag == "nationality":
                    nation_url = stat.find("a")
                    if nation_url:
                        nation_url= nation_url["href"]
                        player_nation = extract_player_nation(nation_url)  #PLAYER NATION
                    else:   
                        player_nation = None
                
# GET PLAYER TEAM

                elif stat_tag == "team":
                    team_name = stat.get_text()
                    team_url = stat.find("a")
                    if team_url:
                        team_url = team_url["href"]
                        team_id = extract_team_id(team_url) 
                    else:
                        team_id = None

# GET PLAYER AGE
                elif stat_tag == "age":
                    player_age = stat.get_text()
                    player_age = player_age[:2]
                    player_age = int(player_age) if player_age.isdigit() else player_age

# ADD PLAYER TO DICTIONARY
                
            add_player_to_dictionary(
                players_dict, player_id, player_name, player_nation, team_id, team_name, season, player_age
            )
    
# GET SEASON

league_urls = [
        "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
        #"https://fbref.com/en/comps/12/stats/La-Liga-Stats",
        #"https://fbref.com/en/comps/11/stats/Serie-A-Stats",
        #https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
        #"https://fbref.com/en/comps/13/stats/Ligue-1-Stats"
]
players_dict = {}
get_stat_urls(league_urls)
get_table_data(league_urls, players_dict)
print(f"Total players found: {len(players_dict)}")
print(json.dumps(players_dict, indent=4))
