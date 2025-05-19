players = []
teams = []
seasons = []
leagues = []
postions = []
player_team_seasons = []

input_file = r"C:\Users\zack2\OneDrive\Documents\GitHub\The-Separation-Game\fbref_players copy.txt"
output_file = r"C:\Users\zack2\OneDrive\Documents\GitHub\The-Separation-Game\formatted_data.txt"

file = open(input_file, "w")

def add_player(player):
    
    if player not in players:
        ############## ADDING PLAYER TO THE LIST ##################
        players.append(player)
        
    players.append(player)

def add_team(team):
    
    teams.append(team)


def add_season(season):

    seasons.append(season)

def add_league(league):

    leagues.append(league)


def add_postion(postion):

    postions.append(postion)


def add_player_team_season(player_team_season):

    player_team_seasons.append(player_team_season)

"""{
    "774cf58b": {
        "player_info": {
            "name": "Max Aarons",
            "nation": "England",
            "age": 25,
            "postions": [
                "Defender",
                "Midfielder"
            ]
        },
        "seasons_played": {
            "2024-2025": {
                "teams": {
                    "Bournemouth": "4ba7cbea",
                    "Valencia": "dcc91a7b"
                }
            },
            "2023-2024": {
                "teams": {
                    "Bournemouth": "4ba7cbea"
                }
            },
            "2021-2022": {
                "teams": {
                    "Norwich City": "1c781004"
                }
            },
            "2019-2020": {
                "teams": {
                    "Norwich City": "1c781004"
                }

                """




