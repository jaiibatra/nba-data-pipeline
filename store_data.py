import sqlite3

from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster


def fetch_team_roster(team_abbreviation, season):
    """Given a team's abbreviation (like 'GSW') and a season (like '2023-24'),
    returns a pandas DataFrame of that team's roster."""

    nba_teams = teams.get_teams()
    matching_teams = [team for team in nba_teams if team['abbreviation'] == team_abbreviation]
    team_id = matching_teams[0]['id']

    roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
    players_df = roster.get_data_frames()[0]

    return players_df


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


# --- Set up the database (this must happen BEFORE we call insert_players) ---

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

cursor.execute("Select name From sqlite_master Where type='table'")
print(cursor.fetchall())

# Clear the whole table once, before inserting all 30 teams fresh
cursor.execute("DELETE FROM players")
conn.commit()

# --- Fetch and insert every team's roster ---

nba_teams = teams.get_teams()

for team in nba_teams:
    print(f"Fetching {team['full_name']}...")
    try:
        players_df = fetch_team_roster(team['abbreviation'], '2023-24')
        insert_players(players_df)
    except Exception as error:
        print(f" Failed to fetch {team['full_name']}: {error}")

conn.commit()

# --- Verify everything got stored correctly ---

cursor.execute("Select * From players")
all_players = cursor.fetchall()
print(f"Total players stored: {len(all_players)}")
for row in all_players:
    print(row)