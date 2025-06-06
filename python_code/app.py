from flask import Flask, request, jsonify
from flask_cors import CORS
from game_logic import initialize_game_data, find_player_connections
import mysql.connector
app = Flask(__name__)
CORS(app)  # ✅ Allow cross-origin requests

graph, player_meta, name_to_id = initialize_game_data()


@app.route('/connect', methods=['POST'])
def connect_players():
    data = request.get_json()

    player_a = data.get("player_a", "").strip()
    player_b = data.get("player_b", "").strip()

    if not player_a or not player_b:
        return jsonify({"error": "Both player names are required."}), 400

    result = find_player_connections(player_a, player_b, graph, player_meta, name_to_id)

    return jsonify(result)

@app.route('/filters', methods=['GET'])
def get_filters():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='7410',
        database='the_separation_game'
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT l.league_name, t.team_name, p.player_name
        FROM player_team_seasons pts
        JOIN players p ON pts.player_id = p.player_id
        JOIN teams t ON pts.team_id = t.team_id
        JOIN leagues l ON t.league_id = l.league_id
        GROUP BY l.league_name, t.team_name, p.player_name
    """)
    
    raw = cursor.fetchall()
    conn.close()

    filters = {}
    for row in raw:
        league = row['league_name']
        team = row['team_name']
        player = row['player_name']

        filters.setdefault(league, {}).setdefault(team, set()).add(player)

    # Convert sets to sorted lists
    for league in filters:
        for team in filters[league]:
            filters[league][team] = sorted(list(filters[league][team]))

    return jsonify(filters)


if __name__ == '__main__':
    app.run(debug=True)
