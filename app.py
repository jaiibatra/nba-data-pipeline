import streamlit as st
import sqlite3

st.title("My NBA Dashboard")

conn = sqlite3.connect('nba.db')
cursor = conn.cursor()

cursor.execute("SELECT player_name FROM players ORDER BY player_name")
players = cursor.fetchall()

player_names = [row[0] for row in players]

selected_player = st.selectbox("Choose a player:", player_names)

cursor.execute('''
    Select players.position, players.height, players.weight, player_stats.points, player_stats.rebounds, player_stats.assists,
        player_stats.fg_pct
    From players
    Join player_stats ON players.player_id = player_stats.player_id
    Where players.player_name = ?
''', (selected_player,))

result = cursor.fetchone()

if result:
    position, height, weight, points, rebounds, assists, fg_pct = result

    st.subheader(selected_player)
    st.write(f"Position: {position} | Height: {height} | Weight: {weight} lbs")

    col1, col2, col3 = st.columns(3)
    col1.metric("Points", points)
    col2.metric("Rebounds", rebounds)
    col3.metric("Assists", assists)

    st.write(f"Field Goal %: {fg_pct:.1%}")
else:
    st.write("No stats found for this player.")