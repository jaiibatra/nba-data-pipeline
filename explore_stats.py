import sqlite3

from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import leaguedashplayerstats


def fetch_team_roster(team_abbreviation, season):
    """Given a team's abbreviation (like 'GSW') and a season (like '2023-24'),
    returns a pandas DataFrame of that team's roster."""
    nba_teams = teams.get_teams()
    matching_teams = [team for team in nba_teams if team['abbreviation'] == team_abbreviation]
    team_id = matching_teams[0]['id']

    roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
    players_df = roster.get_data_frames()[0]

    return players_df


def fetch_league_stats(season):
    """Returns a DataFrame of every player's stats for the given season, league-wide.
    Fetching league-wide (instead of per-team) avoids duplicate rows for players
    who were traded mid-season."""
    stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season, timeout = 60)
    return stats.get_data_frames()[0]


def insert_players(players_df):
    """Takes a DataFrame of players and inserts every row into the players table."""
    for index, player in players_df.iterrows():
        cursor.execute('''
            INSERT INTO players (player_id, player_name, position, height, weight, age, experience)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(player['PLAYER_ID']),
            player['PLAYER'],
            player['POSITION'],
            player['HEIGHT'],
            int(player['WEIGHT']),
            float(player['AGE']),
            player['EXP']
        ))


def insert_stats(stats_df, season):
    """Takes a DataFrame of player stats and inserts every row into the player_stats table."""
    for index, player in stats_df.iterrows():
        cursor.execute('''
            INSERT INTO player_stats (
                player_id, season, games_played, minutes, points,
                rebounds, assists, steals, blocks, turnovers,
                fg_pct, fg3_pct, ft_pct
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(player['PLAYER_ID']),
            season,
            int(player['GP']),
            float(player['MIN']),
            int(player['PTS']),
            int(player['REB']),
            int(player['AST']),
            int(player['STL']),
            int(player['BLK']),
            int(player['TOV']),
            float(player['FG_PCT']),
            float(player['FG3_PCT']),
            float(player['FT_PCT'])
        ))


# --- Set up the database ---

conn = sqlite3.connect('nba.db')
cursor = conn.cursor()

cursor.execute('''
    Create Table IF NOT EXISTS players(
        player_id INT Primary key,
        player_name TEXT,
        position TEXT,
        height TEXT,
        weight INT,
        age REAL,
        experience TEXT
    )
''')

cursor.execute('''
    Create Table if Not Exists player_stats (
        player_id INT,
        season TEXT,
        games_played INT,
        minutes REAL,
        points INT,
        rebounds INT,
        assists INT,
        steals INT,
        blocks INT,
        turnovers INT,
        fg_pct REAL,
        fg3_pct REAL,
        ft_pct REAL,
        PRIMARY KEY(player_id, season)
    )
''')

# --- Fetch and insert everything ---

SEASON = '2023-24'

cursor.execute("DELETE FROM players")
cursor.execute("DELETE FROM player_stats")
conn.commit()

nba_teams = teams.get_teams()

# Fetch all player stats league-wide, once, up front (avoids per-team trade duplicates)
print("Fetching league-wide player stats...")
stats_df = fetch_league_stats(SEASON)
insert_stats(stats_df, SEASON)
conn.commit()

# Fetch each team's roster individually (rosters don't have the trade-duplication issue)
for team in nba_teams:
    print(f"Fetching {team['full_name']} roster...")
    try:
        players_df = fetch_team_roster(team['abbreviation'], SEASON)
        insert_players(players_df)
    except Exception as error:
        print(f"  Failed to fetch {team['full_name']}: {error}")

conn.commit()

# --- Verify everything got stored correctly ---

cursor.execute("SELECT COUNT(*) FROM players")
print(f"Total players stored: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM player_stats")
print(f"Total stat rows stored: {cursor.fetchone()[0]}")

# --- League-wide scoring leaders, combining both tables ---

cursor.execute('''
    SELECT players.player_name, player_stats.points, player_stats.rebounds, player_stats.assists
    FROM players
    JOIN player_stats ON players.player_id = player_stats.player_id
    ORDER BY player_stats.points DESC
    LIMIT 15
''')

print("\nTop 15 scorers league-wide:")
for row in cursor.fetchall():
    print(row)