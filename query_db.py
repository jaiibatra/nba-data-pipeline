import sqlite3

conn = sqlite3.connect('nba.db')
cursor = conn.cursor()

cursor.execute("Select Count(*) From players")
print("Total players: ", cursor.fetchone()[0])

player_name = "Stephen Curry"

cursor.execute('''
    SELECT players.player_name, players.position, players.height, players.weight,
           player_stats.points, player_stats.rebounds, player_stats.assists
    FROM players
    JOIN player_stats ON players.player_id = player_stats.player_id
    WHERE players.player_name = ?
''', (player_name,))

result = cursor.fetchone()
print(result)