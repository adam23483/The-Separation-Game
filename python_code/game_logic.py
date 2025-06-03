import mysql.connector
from collections import defaultdict, deque

def find_k_paths(graph, start, goal, k=5, max_depth=5):
    all_paths = []
    queue = deque([(start, [start])])
    seen_paths = set()

    while queue and len(all_paths) < k:
        current, path = queue.popleft()
        if current == goal:
            path_tuple = tuple(path)
            if path_tuple not in seen_paths:
                seen_paths.add(path_tuple)
                all_paths.append(path)
            continue
        if len(path) > max_depth:
            continue
        for neighbor in graph[current]:
            if neighbor not in path:
                queue.append((neighbor, path + [neighbor]))
    return all_paths

def display_path_details(path, player_meta):
    details = []
    for player_id in path:
        record = player_meta[player_id][0]  # First occurrence (can be improved to best-match later)
        season_range = record['season_range']
        details.append(f"{record['name']} ({record['team']}, {record['league']}, {season_range})")
    return " → ".join(details)

# Connect to DB
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='7410',
    database='the_separation_game'
)
cursor = conn.cursor(dictionary=True)

# Step 1: Get season_id → season string
cursor.execute("SELECT season_id, season FROM seasons")
season_map = {row['season_id']: row['season'] for row in cursor.fetchall()}

# Step 2: Get all player-team-season data
cursor.execute("""
    SELECT pts.player_id, p.player_name, t.team_name, l.league_name, pts.season_id, pts.team_id
    FROM player_team_seasons pts
    JOIN players p ON pts.player_id = p.player_id
    JOIN teams t ON pts.team_id = t.team_id
    JOIN leagues l ON t.league_id = l.league_id
""")
rows = cursor.fetchall()

# Track teammates by team+season
graph = defaultdict(set)
team_season_players = defaultdict(list)

# Player metadata with ranges
player_meta = defaultdict(list)
player_team_seasons = defaultdict(set)

# Step 3: Populate structures
for row in rows:
    season_name = season_map.get(row['season_id'], f"Season {row['season_id']}")
    player_id = row['player_id']
    team_id = row['team_id']
    key = (team_id, row['season_id'])
    team_season_players[key].append(player_id)
    player_team_seasons[(player_id, team_id)].add(season_name)

# Step 4: Compute ranges
player_team_ranges = {}
for (player_id, team_id), seasons in player_team_seasons.items():
    sorted_seasons = sorted(seasons)
    season_range = f"{sorted_seasons[0]} to {sorted_seasons[-1]}" if len(sorted_seasons) > 1 else sorted_seasons[0]
    player_team_ranges[(player_id, team_id)] = season_range

# Step 5: Re-scan rows to build metadata
for row in rows:
    player_id = row['player_id']
    team_id = row['team_id']
    player_meta[player_id].append({
        "name": row['player_name'],
        "team": row['team_name'],
        "league": row['league_name'],
        "season_range": player_team_ranges[(player_id, team_id)]
    })

# Step 6: Build graph
for players in team_season_players.values():
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            graph[players[i]].add(players[j])
            graph[players[j]].add(players[i])

# Step 7: Name → ID map
name_to_id = {}
for player_id, entries in player_meta.items():
    for entry in entries:
        name_to_id[entry['name'].lower()] = player_id

# Step 8: Input
player_a = input("Enter first player name: ").strip().lower()
player_b = input("Enter second player name: ").strip().lower()

if player_a not in name_to_id or player_b not in name_to_id:
    print("One or both players not found.")
else:
    id_a = name_to_id[player_a]
    id_b = name_to_id[player_b]

    paths = find_k_paths(graph, id_a, id_b, k=5)
    if paths:
        print(f"\nTop {len(paths)} paths:")
        for i, path in enumerate(paths, 1):
            print(f"{i}. {display_path_details(path, player_meta)} (Links: {len(path) - 1})")
    else:
        print("No connection found between those players.")
