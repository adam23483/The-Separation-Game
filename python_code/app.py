from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from game_logic import initialize_game_data, find_player_connections, display_path_details, find_k_paths
from daily_challenge_manager import get_challenges, DAILY_FILE
from datetime import datetime, timedelta
import json 
import mysql.connector
import random
import os
import hashlib


app = Flask(__name__, static_folder='../website/public', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Guided mode in-memory cache

# Cache for game data and daily challenges
_game_cache = {
    "graph": None,
    "player_meta": None,
    "name_to_id": None
}
_guided_cache = {}

def _generate_guided_cache_key(current_path, player_b):
    base = json.dumps({"path": current_path, "target": player_b}, sort_keys=True)
    return hashlib.md5(base.encode()).hexdigest()

def get_game_data():
    if _game_cache["graph"] is None:
        graph, player_meta, name_to_id = initialize_game_data()
        _game_cache["graph"] = graph
        _game_cache["player_meta"] = player_meta
        _game_cache["name_to_id"] = name_to_id
    return _game_cache["graph"], _game_cache["player_meta"], _game_cache["name_to_id"]

@app.route('/guided_next_moves', methods=['POST'])
def guided_next_moves():
    data = request.get_json()
    current_path = data.get('current_path', [])
    player_b = data.get('player_b', '').lower().strip()

    if not current_path or not player_b:
        return jsonify({"error": "Invalid input"}), 400

    step_index = len(current_path) - 1  # Each move corresponds to a step
    try:
        with open(DAILY_FILE, "r") as f:
            daily_data = json.load(f)
    except Exception as e:
        return jsonify({"error": "Could not load challenge data."}), 500

    # Locate the challenge that matches this player A → player B
    for pair in daily_data["pairs"]:
        if (pair["player_a"]["name"].lower() == current_path[0].lower() and
            pair["player_b"]["name"].lower() == player_b):

            guided_steps = pair.get("guided_steps", [])
            if step_index < len(guided_steps):
                return jsonify({"options": guided_steps[step_index]["options"]})
            else:
                return jsonify({"error": "No more steps available."}), 404

    return jsonify({"error": "No matching challenge found."}), 404


@app.route('/connect', methods=['POST'])
def connect_players():
    data = request.get_json()
    player_a = data.get('player_a', '').lower().strip()
    player_b = data.get('player_b', '').lower().strip()

    if not player_a or not player_b:
        return jsonify({"error": "Both players must be provided."}), 400

    graph, player_meta, name_to_id = get_game_data()

    if player_a not in name_to_id or player_b not in name_to_id:
        return jsonify([])

    paths = find_player_connections(player_a, player_b, graph, player_meta, name_to_id, k=5)

    if isinstance(paths, dict) and 'error' in paths:
        return jsonify({"error": paths['error']}), 400
    if isinstance(paths, dict) and 'message' in paths:
        return jsonify([])

    response = []
    for p in paths:
        details = display_path_details(p['path'], player_meta)  # Now called correctly on raw ID path
        path_segments = []
        for d in details:
            # 'd' is already formatted text
            path_segments.append(d)
        response.append({
            "path": ' → '.join(path_segments),
            "links": p['links']
        })

    return jsonify(response)
    

@app.route('/daily_challenges', methods=['GET'])
def daily_challenges():
    print("[API CALL] /daily_challenges endpoint hit.")
    challenge_data = get_challenges()
    print(f"[API RESPONSE] /daily_challenges returning {len(challenge_data['pairs'])} pairs. Expires at: {challenge_data['expires']}")
    return jsonify({
        "pairs": challenge_data['pairs'],
        "expires": challenge_data['expires'],
        "start": challenge_data['start']
    })

@app.route('/filters', methods=['GET'])
def get_filters():
    print("[API CALL] /filters endpoint hit. Querying database...")
    conn = mysql.connector.connect(
        host='localhost', user='root', password='7410', database='the_separation_game')
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT l.league_name, t.team_name, p.player_name, s.season
        FROM player_team_seasons pts
        JOIN players p ON pts.player_id = p.player_id
        JOIN teams t ON pts.team_id = t.team_id
        JOIN leagues l ON t.league_id = l.league_id
        JOIN seasons s ON pts.season_id = s.season_id
        GROUP BY l.league_name, t.team_name, p.player_name, s.season
    """)
    raw = cursor.fetchall()
    conn.close()
    print(f"[API RESPONSE] /filters returning {len(raw)} entries from database.")

    filters = {}
    for row in raw:
        league = row['league_name']
        team = row['team_name']
        season = row['season']
        player = row['player_name']
        filters.setdefault(league, {}).setdefault(team, {}).setdefault(season, set()).add(player)

    # Convert sets to sorted lists for JSON serializability
    for league in filters:
        for team in filters[league]:
            for season in filters[league][team]:
                filters[league][team][season] = sorted(list(filters[league][team][season]))

    print(f"[API RESPONSE] /filters structured response contains {len(filters)} leagues.")
    return jsonify(filters)

@app.route('/random_pair', methods=['GET'])
def random_pair():
    graph, player_meta, name_to_id = get_game_data()
    player_ids = list(player_meta.keys())
    if len(player_ids) < 2:
        return jsonify({"error": "Not enough players in database."})
    id_a, id_b = random.sample(player_ids, 2)

    def get_team_summary(pid):
        records = player_meta[pid]
        summary = {}
        for r in records:
            key = (r['team'], r['league'])
            summary.setdefault(key, set()).add(r['season_range'])
        return [
            {"team": team, "league": league, "years": " to ".join(sorted(ranges))}
            for (team, league), ranges in summary.items()
        ]

    return jsonify({
        "player_a": {"name": player_meta[id_a][0]['name'], "teams": get_team_summary(id_a)},
        "player_b": {"name": player_meta[id_b][0]['name'], "teams": get_team_summary(id_b)}
    })
    


@app.route('/score_challenge', methods=['POST'])
def score_challenge():
    data = request.get_json()
    raw_path = data.get('path', '')
    player_a = data.get('player_a', '').lower().strip()
    player_b = data.get('player_b', '').lower().strip()
    time_count = int(data.get('time', 0))
    players = [p.strip() for p in raw_path.split('→')]

    graph, player_meta, name_to_id = get_game_data()

    ids = []
    for p in players:
        pid = name_to_id.get(p.lower())
        if not pid:
            return jsonify({"error": f"Invalid player name: {p}"}), 400
        ids.append(pid)

    user_links_count = len(ids) - 1

    link_validity = []
    for i in range(user_links_count):
        a, b = ids[i], ids[i+1]
        valid = b in graph[a]
        link_validity.append({
            "from": player_meta[a][0]["name"],
            "to": player_meta[b][0]["name"],
            "valid": valid
        })

    min_paths = find_player_connections(player_a, player_b, graph, player_meta, name_to_id, k=3)
    min_links_count = min([p['links'] for p in min_paths]) if min_paths else user_links_count
    lost_point_value = 10
    lost_time_value = 0.05
    starting_score = 100
    link_points_lost = lost_point_value * max(0, user_links_count - min_links_count)
    time_points_lost = lost_time_value * time_count
    final_score = starting_score - link_points_lost - time_points_lost

    alternatives = [{"path": p['path'].replace('\n', ' → '), "links": p['links']} for p in min_paths]

    return jsonify({
        "cleaned_path": players,
        "user_links_count": user_links_count,
        "min_links_count": min_links_count,
        "link_points_lost": link_points_lost,
        "time_points_lost": round(time_points_lost, 2),
        "final_score": round(final_score, 2),
        "time_count": time_count,
        "alternatives": alternatives,
        "link_breakdown": link_validity
    })

if __name__ == '__main__':
    app.run(debug=False)
