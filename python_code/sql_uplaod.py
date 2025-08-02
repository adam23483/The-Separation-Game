import json
import mysql.connector

# connection setup
conn = mysql.connector.connect(
    host='localhost',      
    user='root',    
    password='7410',
    database='the_separation_game' 
)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS player_team_seasons;")
cursor.execute("DROP TABLE IF EXISTS seasons;")
cursor.execute("DROP TABLE IF EXISTS teams;")
cursor.execute("DROP TABLE IF EXISTS players;")
cursor.execute("DROP TABLE IF EXISTS leagues;")
cursor.execute("DROP TABLE IF EXISTS positions;")

# add JSON data
with open('C:\\Users\\zack2\\OneDrive\\Documents\\GitHub\\The-Separation-Game\\json_data\\processed_fbref_data.json', 'r') as f:
    data = json.load(f)

# Process seasons to split ranges into individual years
season_range_to_ids = {}
new_seasons = []
new_season_id = 1

for season_entry in data['seasons']:
    season_range = season_entry['season']  # e.g., '2025-2026'
    start_year, end_year = map(int, season_range.split('-'))

    # Add start year
    season_range_to_ids[(season_entry['season_id'], start_year)] = new_season_id
    new_seasons.append({"season_id": new_season_id, "season": str(start_year)})
    new_season_id += 1

    # Add end year
    season_range_to_ids[(season_entry['season_id'], end_year)] = new_season_id
    new_seasons.append({"season_id": new_season_id, "season": str(end_year)})
    new_season_id += 1

# Replace seasons with expanded ones
data['seasons'] = new_seasons

# Rebuild player_team_seasons to reference individual seasons and include position_id and league_id
new_player_team_seasons = []
pts_id = 1

player_id_to_position = {player['player_id']: player['player_positions'] for player in data['players']}
team_id_to_league = {team['team_id']: team['league_id'] for team in data['teams']}

for pts in data['player_team_seasons']:
    original_season_id = pts['season_id']
    player_id = pts['player_id']
    team_id = pts['team_id']

    position_id = player_id_to_position.get(player_id)
    league_id = team_id_to_league.get(team_id)

    for (orig_id, year), new_id in season_range_to_ids.items():
        if orig_id == original_season_id:
            new_entry = {
                'player_team_season_id': pts_id,
                'player_id': player_id,
                'team_id': team_id,
                'season_id': new_id,
                'position_id': position_id,
                'league_id': league_id
            }
            new_player_team_seasons.append(new_entry)
            pts_id += 1

data['player_team_seasons'] = new_player_team_seasons

# create tables if they don't exist
table_definitions = {
    "leagues": """
        CREATE TABLE IF NOT EXISTS leagues (
            league_id INT PRIMARY KEY,
            league_name VARCHAR(255)
        )
    """,
    "teams": """
        CREATE TABLE IF NOT EXISTS teams (
            team_id INT PRIMARY KEY,
            team_name VARCHAR(255),
            team_ext_id VARCHAR(32),
            league_id INT,
            FOREIGN KEY (league_id) REFERENCES leagues(league_id)
        )
    """,
    "seasons": """
        CREATE TABLE IF NOT EXISTS seasons (
            season_id INT PRIMARY KEY,
            season VARCHAR(32)
        )
    """,
    "positions": """
        CREATE TABLE IF NOT EXISTS positions (
            position_id INT PRIMARY KEY,
            position VARCHAR(64)
        )
    """,
    "players": """
        CREATE TABLE IF NOT EXISTS players (
            player_id  INT PRIMARY KEY,
            player_name VARCHAR(255),
            player_ext_id VARCHAR(32),
            player_nation VARCHAR(64),
            player_age INT,
            player_positions INT,
            FOREIGN KEY (player_positions) REFERENCES positions(position_id)
        )
    """,
    "player_team_seasons": """
        CREATE TABLE IF NOT EXISTS player_team_seasons (
            player_team_season_id INT PRIMARY KEY,
            player_id INT,
            team_id INT,
            season_id INT,
            position_id INT,
            league_id INT,
            FOREIGN KEY (player_id) REFERENCES players(player_id),
            FOREIGN KEY (team_id) REFERENCES teams(team_id),
            FOREIGN KEY (season_id) REFERENCES seasons(season_id),
            FOREIGN KEY (position_id) REFERENCES positions(position_id),
            FOREIGN KEY (league_id) REFERENCES leagues(league_id)
        )
    """
}

# insert data into a table
def insert_data(table_name, records):
    if not records:
        print(f"No data to insert for table {table_name}")
        return

    columns = records[0].keys()
    placeholders = ', '.join(['%s'] * len(columns))
    column_names = ', '.join(columns)
    sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

    values = [tuple(record[col] for col in columns) for record in records]
    cursor.executemany(sql, values)
    print(f"Inserted {cursor.rowcount} rows into {table_name}")

# create tables
for table_name, ddl in table_definitions.items():
    cursor.execute(ddl)
    print(f"Ensured table exists: {table_name}")

# insert data
insert_data('positions', data.get('positions', []))
insert_data('leagues', data.get('leagues', []))
insert_data('teams', data.get('teams', []))
insert_data('seasons', data.get('seasons', []))
insert_data('players', data.get('players', []))
insert_data('player_team_seasons', data.get('player_team_seasons', []))

# commit and close
conn.commit()
cursor.close()
conn.close()
