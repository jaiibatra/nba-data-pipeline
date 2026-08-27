from nba_api.stats.static import teams

nba_teams = teams.get_teams()

# print(nba_teams)

# Returns as a list of 30 boxes and every box has 7 labels with id, full_name, city and all that about the team. 

# Looking at one team which is the first one in the list.
first_team = nba_teams[0]
#print(first_team)

# Grabbing one label from the dictionary.
#print(first_team['full_name'])

# Picking favorite team
warriors = []
for team in nba_teams:
    if team ['abbreviation'] == 'GSW':
        warriors.append(team)

print(warriors)
print()

# Team id since we want to be specific
warriors_team = warriors[0] # Holds all the information on the warriors
warriors_id = warriors_team['id'] # Specifically chooses the id value from the dictionary
print(warriors_id)

# Now we want to actually reach out to the api of the nba
from nba_api.stats.endpoints import commonteamroster

# Ask the api for the teams roster
roster = commonteamroster.CommonTeamRoster(team_id=warriors_id, season='2023-24')
print(roster)
# This prints where the object is living in memory (internal address), its like a mail we recieved but havent opened yet.

# Now we ask the object for its data
data_frames = roster.get_data_frames() # "Opening the envelope" -> COnverting the sealed information into pandas DataFrame
print(len(data_frames)) # This returned 2 which means we got back two seperate tables 

# To print out column names to see which one is actually the roster table

players_df = data_frames[0]
coaches_df = data_frames[0]

print("Table 0 shape:", players_df.shape)
print("Table 1 shape:", coaches_df.shape)
print()
print("--- Table 0, first 3 rows ---")
print(players_df.head(3))
print()
print("--- Table 1, first 3 rows ---")
print(coaches_df.head(3))


# We only need players_df going forward — the second table was a duplicate
print(players_df[['PLAYER', 'POSITION', 'HEIGHT', 'WEIGHT', 'AGE', 'EXP']])