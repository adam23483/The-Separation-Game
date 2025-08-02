from datetime import datetime, timedelta
import os
import json
from game_logic import initialize_game_data
import random  # You forgot to import this in your last upload

DAILY_FILE = "C:\\Users\\zack2\\OneDrive\\Documents\\GitHub\\The-Separation-Game\\python_code\\daily_challenges.json"

def get_challenges():
    now = datetime.utcnow()

    # Check if cache file exists and is valid
    if os.path.exists(DAILY_FILE):
        if os.path.getsize(DAILY_FILE) > 0:
            try:
                with open(DAILY_FILE, "r") as f:
                    data = json.load(f)
                    expires_at = datetime.fromisoformat(data["expires"])
                    print(f"[DEBUG] Cached challenges expire at: {expires_at} (UTC)")
                    if now < expires_at:
                        print("[DEBUG] Returning cached daily challenges (still valid).")
                        return data
                    else:
                        print("[DEBUG] Cached challenges expired. Generating new set.")
            except json.JSONDecodeError:
                print("[ERROR] Cache file is corrupt. Regenerating challenges.")
        else:
            print("[ERROR] Cache file exists but is empty. Regenerating challenges.")
    else:
        print("[DEBUG] Cache file does not exist. Generating new challenges.")

    # Generate new challenges
    print("[DEBUG] Loading game data to generate new daily challenges...")
    graph, player_meta, _ = initialize_game_data()

    print(f"[DEBUG] player_meta entries count: {len(player_meta)}")
    if len(player_meta) < 2:
        print("[ERROR] Not enough players to generate challenges.")
        return {"pairs": [], "expires": now.isoformat(), "start": now.isoformat()}

    # Generate raw pairs
    player_ids = list(player_meta.keys())
    pairs = []
    for _ in range(3):
        id_a, id_b = random.sample(player_ids, 2)
        pairs.append((id_a, id_b))
    print(f"[DEBUG] Generated {len(pairs)} raw player pairs for daily challenges.")

    # Format pair data
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
                if len(sorted_seasons) == 1:
                    season_range = sorted_seasons[0]
                else:
                    season_range = f"{sorted_seasons[0]} to {sorted_seasons[-1]}"
                formatted_teams.append({
                    "team": team,
                    "league": league,
                    "season_range": season_range
                })
            return formatted_teams

        a_teams = team_summary(pid_a)
        b_teams = team_summary(pid_b)
        a_meta = player_meta[pid_a][0]
        b_meta = player_meta[pid_b][0]

        formatted.append({
            "player_a": {
                "name": a_meta['name'],
                "teams": a_teams
            },
            "player_b": {
                "name": b_meta['name'],
                "teams": b_teams
            },
            "path": f"{a_meta['name']} ({a_teams[0]['team']}, {a_teams[0]['league']}, {a_teams[0]['season_range']}) → {b_meta['name']} ({b_teams[0]['team']}, {b_teams[0]['league']}, {b_teams[0]['season_range']})"
        })

    print(f"[DEBUG] Formatted {len(formatted)} challenge pairs.")

    expiry = (now + timedelta(days=1)).isoformat()
    result = {"pairs": formatted, "expires": expiry, "start": now.isoformat()}

    # Write to cache file
    with open(DAILY_FILE, "w") as f:
        json.dump(result, f)
    print(f"[DEBUG] Saved daily challenges to cache file: {DAILY_FILE}")

    return result
