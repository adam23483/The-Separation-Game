# The Separation Game

A soccer-based trivia and strategy web game where players try to connect two professional footballers through the shortest path of shared teammates, based on overlapping team history.
## Working player link search HTML
![image](https://github.com/adam23483/The-Separation-Game/blob/f44ae8eb2f84aece219f23a663e2462e3cc36ac6/Images/testing%20api.png)

## Game Objective

Connect two players using the fewest possible intermediate player links (players who were teammates of both targets at different points in time).

## Gameplay

- Core Challenge: Build a chain of player connections from Player A to Player B through overlapping club seasons.
- At least one player must link the two.
- Bonus Challenges:
  - Identify an additional player that could link them
  - Guess their manager during overlapping years
  - Add players that would also form valid paths
- Side Games:
  - "Did they play on the same team?"
  - "Who was their manager?"

## Example Challenge

**Goal**: Connect Ronaldinho to Kylian Mbappé

### Solution 1 (Shortest Path)
```
Ronaldinho → Lionel Messi → Kylian Mbappé  
(1 player link)
```

### Solution 2 (Alternate Path)
```
Ronaldinho → Kaká → Luka Modrić → Kylian Mbappé  
(3 player links)
```

## Scoring System

- Starting Score: 100 points  
- Points Lost for Extra Links: -10 per additional player link  
- Points Lost Over Time: -0.05 per second  

### Example:
- Your solution: 5 links (min was 2)
- Time taken: 300 seconds

```
Link penalty: (5 - 2) * 10 = 30  
Time penalty: 300 * 0.05 = 15  
Final score: 100 - 30 - 15 = 55
```

## Bonus Points

- +10 points for identifying a manager for each link
- Partial points for accurate year ranges (based on percentage of correct years)

## Data and Architecture

### Sources:
- FBref
- Transfermarkt
- Wikipedia

### Focus Areas:
- Top 5 European Leagues: Premier League, La Liga, Bundesliga, Ligue 1, Serie A
- Expand to: South America, Africa, Asia, etc.

### Tech Stack:
- Python
- JavaScript / Node.js
- SQL (local, then AWS/Google Cloud)
- Web Scraping
- GenAI integrations (optional)
- Frontend UI (lightweight, user-friendly)
- Leaderboards, group sessions, and login system

## Schema & Database Design

### Schema
![image](https://github.com/adam23483/The-Separation-Game/blob/240965e1cc904b51b18a871da613bd9c238e6de2/Images/Schema.png)


Key Tables:
- `players`
- `teams`
- `leagues`
- `seasons`
- `player_team_season`
- `positions`
- `nations`

Includes appearance tracking, loan filters, January transfers, and historical changes (e.g., country splits).

## Future Expansion

- Add NFL, NBA, MLB, NHL versions
- Expand player tracking to college/high school
- Possible spin-off sites for each sport
