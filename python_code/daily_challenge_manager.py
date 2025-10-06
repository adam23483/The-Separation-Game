from datetime import datetime, timedelta
import os
import json
from game_logic import initialize_game_data, find_k_paths
import random

DAILY_FILE = "C:\\Users\\zack2\\OneDrive\\Documents\\GitHub\\The-Separation-Game\\python_code\\daily_challenges.json"

def get_challenges():
    now = datetime.utcnow()

    if os.path.exists(DAILY_FILE):
        if os.path.getsize(DAILY_FILE) > 0:
            try:
                with open(DAILY_FILE, "r") as f:
                    data = json.load(f)
                    expires_at = datetime.fromisoformat(data["expires"])
                    if now < expires_at:
                        return data
            except json.JSONDecodeError:
                pass

    graph, player_meta, name_to_id = initialize_game_data()
    player_ids = list(player_meta.keys())
    if len(player_ids) < 2:
        return {"pairs": [], "expires": now.isoformat(), "start": now.isoformat()}

    pairs = []
    for _ in range(3):
        id_a, id_b = random.sample(player_ids, 2)
        pairs.append((id_a, id_b))

    formatted = []
    for pid_a, pid_b in pairs:
        def team_summary(pid):
            summary = {}
            for r in player_meta[pid]:
                key = (r['team'], r['league'])
                summary.setdefault(key, set()).add(r['season_range'])
            formatted_teams = []
            for (team, league), seasons in summary.items():
                sorted_seasons = sorted(seasons)
                season_range = sorted_seasons[0] if len(sorted_seasons) == 1 else f"{sorted_seasons[0]} to {sorted_seasons[-1]}"
                formatted_teams.append({
                    "team": team,
                    "league": league,
                    "season_range": season_range
                })
            return formatted_teams

        a_meta = player_meta[pid_a][0]
        b_meta = player_meta[pid_b][0]
        a_teams = team_summary(pid_a)
        b_teams = team_summary(pid_b)

        path_ids = find_k_paths(graph, pid_a, pid_b, k=1, max_depth=5)
        if not path_ids:
            continue
        path = path_ids[0]

        guided_steps = []
        for i in range(len(path) - 1):
            current_id = path[i]
            next_id = path[i+1]
            current_neighbors = graph[current_id]

            valid_next = []
            for nid in current_neighbors:
                if nid == next_id:
                    valid_next.append(nid)

            # Add a second correct if possible (same degree)
            while len(valid_next) < 2:
                alt = random.choice(list(current_neighbors))
                if alt != current_id and alt != next_id and alt in player_meta:
                    valid_next.append(alt)

            all_ids = set(graph.keys())
            distractors = list(all_ids - set(valid_next) - {current_id})
            distractor_ids = random.sample(distractors, 3)

            option_ids = valid_next[:2] + distractor_ids
            random.shuffle(option_ids)

            options = []
            for oid in option_ids:
                if oid not in player_meta:
                    continue
                entry = player_meta[oid][0]
                history = [{
                    "team": r["team"],
                    "league": r["league"],
                    "season_range": r["season_range"]
                } for r in player_meta[oid]]
                options.append({
                    "name": entry["name"],
                    "team": entry["team"],
                    "league": entry["league"],
                    "season_range": entry["season_range"],
                    "is_correct": oid in valid_next,
                    "team_history": history
                })

            guided_steps.append({
                "from": player_meta[current_id][0]["name"],
                "options": options
            })

        formatted.append({
            "player_a": {
                "name": a_meta['name'],
                "teams": a_teams
            },
            "player_b": {
                "name": b_meta['name'],
                "teams": b_teams
            },
            "path": f"{a_meta['name']} ({a_teams[0]['team']}, {a_teams[0]['league']}, {a_teams[0]['season_range']}) → {b_meta['name']} ({b_teams[0]['team']}, {b_teams[0]['league']}, {b_teams[0]['season_range']})",
            "guided_steps": guided_steps
        })

    expiry = (now + timedelta(days=1)).isoformat()
    result = {"pairs": formatted, "expires": expiry, "start": now.isoformat()}

    with open(DAILY_FILE, "w") as f:
        json.dump(result, f)

    return result
