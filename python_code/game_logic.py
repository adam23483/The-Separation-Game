# --- game_logic.py (Corrected) ---
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
    def linkify(name):
        return f'<a href="https://www.google.com/search?q={name.replace(" ", "+")}" target="_blank">{name}</a>'

    detailed_steps = []
    for i in range(len(path) - 1):
        a_records = player_meta.get(path[i], [])
        b_records = player_meta.get(path[i + 1], [])

        if not a_records or not b_records:
            print(f"[ERROR] Missing metadata for IDs: {path[i]} or {path[i+1]}")
            continue

        a_record = a_records[0]
        b_record = b_records[0]

        shared_team = None
        for a in a_records:
            for b in b_records:
                if a['team'] == b['team'] and a['league'] == b['league']:
                    shared_team = (a, b)
                    break
            if shared_team:
                break

        if shared_team:
            a, b = shared_team
            detailed_steps.append(
                f"{linkify(a['name'])} ({a['team']}, {a['league']}, {a['season_range']}) → {linkify(b['name'])} ({b['team']}, {b['league']}, {b['season_range']})"
            )
        else:
            detailed_steps.append(
                f"{linkify(a_record['name'])} ({a_record['team']}, {a_record['league']}, {a_record['season_range']}) → {linkify(b_record['name'])} ({b_record['team']}, {b_record['league']}, {b_record['season_range']})"
            )

    return detailed_steps

def initialize_game_data():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='7410',
        database='the_separation_game'
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT season_id, season FROM seasons")
    season_map = {row['season_id']: row['season'] for row in cursor.fetchall()}

    cursor.execute("""
        SELECT pts.player_id, p.player_name, t.team_name, l.league_name, pts.season_id, pts.team_id
        FROM player_team_seasons pts
        JOIN players p ON pts.player_id = p.player_id
        JOIN teams t ON pts.team_id = t.team_id
        JOIN leagues l ON t.league_id = l.league_id
    """)
    rows = cursor.fetchall()

    graph = defaultdict(set)
    team_season_players = defaultdict(list)
    player_meta = defaultdict(list)
    player_team_seasons = defaultdict(set)

    for row in rows:
        season_name = season_map.get(row['season_id'], f"Season {row['season_id']}")
        player_id = row['player_id']
        team_id = row['team_id']
        key = (team_id, row['season_id'])

        team_season_players[key].append(player_id)
        player_team_seasons[(player_id, team_id)].add(season_name)

    player_team_ranges = {}
    for (player_id, team_id), seasons in player_team_seasons.items():
        sorted_seasons = sorted(seasons)
        if len(sorted_seasons) == 1:
            season_range = sorted_seasons[0]
        else:
            season_range = f"{sorted_seasons[0]} to {sorted_seasons[-1]}"
        player_team_ranges[(player_id, team_id)] = season_range

    for row in rows:
        player_id = row['player_id']
        team_id = row['team_id']
        player_meta[player_id].append({
            "name": row['player_name'],
            "team": row['team_name'],
            "league": row['league_name'],
            "season_range": player_team_ranges[(player_id, team_id)]
        })

    for players in team_season_players.values():
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                graph[players[i]].add(players[j])
                graph[players[j]].add(players[i])

    name_to_id = {}
    for player_id, entries in player_meta.items():
        for entry in entries:
            name_to_id[entry['name'].lower()] = player_id

    conn.close()
    return graph, player_meta, name_to_id

def find_player_connections(player_a, player_b, graph, player_meta, name_to_id, k=5):
    player_a = player_a.strip().lower()
    player_b = player_b.strip().lower()

    if player_a not in name_to_id or player_b not in name_to_id:
        return {"error": "One or both players not found."}

    id_a = name_to_id[player_a]
    id_b = name_to_id[player_b]

    paths = find_k_paths(graph, id_a, id_b, k=k)

    valid_paths = []
    for path in paths:
        if all(pid in player_meta for pid in path):
            valid_paths.append({
                "path": path,  # Return raw path of IDs
                "links": len(path) - 1
            })

    return valid_paths if valid_paths else {"message": "No connection found."}

