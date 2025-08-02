
# The Separation Game

A web-based soccer connection game where users link two professional footballers through shared teammates, based on real-world club and season history.

![Gameplay Preview](https://github.com/adam23483/The-Separation-Game/blob/9faa2533de7fbc3721b8cb512cea6a3dd3065236/Images/homepage.png)

---

## Table of Contents
- [Objective](#objective)
- [Gameplay Modes](#gameplay-modes)
  - [Daily Challenge](#daily-challenge)
  - [Challenge Mode](#challenge-mode)
  - [Link Lookup](#link-lookup)
  - [Leaderboard (Upcoming)](#leaderboard-upcoming)
- [Scoring System](#scoring-system)
- [Data Sources](#data-sources)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Future Expansion](#future-expansion)

---

## Objective
- Connect **Player A** to **Player B** through mutual teammates.
- Use the fewest possible intermediate players.
- Earn bonus points by identifying shared managers and accurate team-season ranges.

---

## Gameplay Modes
### Daily Challenge
- Three unique player pairs generated daily.
- Time-limited challenge with a global countdown.
- Compete for high scores based on path efficiency and speed.

### Challenge Mode
- Randomly generate two players and manually build a connection path.
- Immediate feedback and scoring.
- Displays alternative valid paths after submission.

### Link Lookup
- Search for connection paths between any two players.
- Explore historical paths without scoring constraints.

### Leaderboard (Upcoming)
- Global leaderboard tracking top scores.
- Daily and all-time rankings planned for future updates.

---

## Scoring System
| Metric              | Penalty/Bonus                   |
|---------------------|---------------------------------|
| Extra Player Links   | -10 points per additional link  |
| Time Taken           | -0.05 points per second         |
| Manager Identified   | +10 points per correct manager  |
| Accurate Year Ranges | Partial points based on accuracy|

### Example Calculation:
```
Starting Score: 100
Your Path: 5 links (Minimum Possible: 2)
Time Taken: 300 seconds

Link Penalty: (5 - 2) * 10 = 30
Time Penalty: 300 * 0.05 = 15

Final Score: 100 - 30 - 15 = 55
```

---

## Data Sources
- FBref (Player appearance data)
- Transfermarkt (Transfers, managers)
- Wikipedia (Historical team data)

Focus Areas:
- Premier League, La Liga, Bundesliga, Serie A, Ligue 1
- Planned expansion to South American, African, and Asian leagues

---

## Tech Stack
- Python (Flask API)
- JavaScript (Frontend interactivity)
- MySQL Database
- Web Scraping pipelines
- HTML/CSS (Tailwind CSS framework)
- Planned: Cloud deployment (AWS or Google Cloud), Leaderboards, Login System

---

## Database Schema
![Database Schema](https://github.com/adam23483/The-Separation-Game/blob/240965e1cc904b51b18a871da613bd9c238e6de2/Images/Schema.png)

Key Tables:
- `players`
- `teams`
- `leagues`
- `seasons`
- `player_team_seasons`
- `positions`
- `nations`

Supports appearance tracking, loans, January transfers, and historical changes (e.g., country splits).

---

## Future Expansion
- Extend to other sports (NBA, NFL, MLB, NHL)
- College and high school player tracking
- Spin-off games/sites for other sports ecosystems
- Enhanced multiplayer and group sessions
- Advanced path scoring with AI-driven suggestions
- Fully featured leaderboard with login authentication
