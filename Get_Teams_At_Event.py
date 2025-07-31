import requests
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import table as pd_table


def get_team_name(team_number, cache):
    if team_number in cache:
        return cache[team_number]
    url = f"https://api.ftcscout.org/rest/v1/teams/{team_number}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        name = data.get('name', 'Unknown')
        cache[team_number] = name
        return name
    return "Unknown"

team_id = int(input("Enter your team ID: "))
year = input("Enter year: ")

# 1. Get all events for your team
url = f"https://api.ftcscout.org/rest/v1/teams/{team_id}/events/{year}"
response = requests.get(url)
events_data = response.json()

df_events = pd.json_normalize(events_data)
df_events = df_events[['eventCode']]
df_events.rename(columns={'eventCode': 'Event'}, inplace=True)
print("\nAvailable Events:")
print(df_events)

# 2. Let user pick an event
event_index = int(input("Select an event index from above: "))
event_code = df_events.iloc[event_index]['Event']

# 3. Get all matches for that event
url_matches = f"https://api.ftcscout.org/rest/v1/events/{year}/{event_code}/matches"
response = requests.get(url_matches)
matches_data = response.json()

# 4. Cache for team names
team_name_cache = {}

# 5. Filter and extract match info
relevant_matches = []

for i, match in enumerate(matches_data):
    teams = match['teams']

    if team_id not in [team['teamNumber'] for team in teams]:
        continue

    my_team = next(team for team in teams if team['teamNumber'] == team_id)
    my_alliance = my_team['alliance']

    # Team groups
    alliance_teams = [t['teamNumber'] for t in teams if t['alliance'] == my_alliance]
    opponent_teams = [t['teamNumber'] for t in teams if t['alliance'] != my_alliance]
    partner = [t for t in alliance_teams if t != team_id]

    match_entry = {
        'Match': f"Q{i+1}",
        'Alliance': my_alliance,
        'Your Team': f"{team_id} ({get_team_name(team_id, team_name_cache)})",
        'Partner': f"{partner[0]} ({get_team_name(partner[0], team_name_cache)})" if partner else "N/A",
        'Opponent 1': f"{opponent_teams[0]} ({get_team_name(opponent_teams[0], team_name_cache)})",
        'Opponent 2': f"{opponent_teams[1]} ({get_team_name(opponent_teams[1], team_name_cache)})",
    }

    relevant_matches.append(match_entry)

# 6. Display final table
df_results = pd.DataFrame(relevant_matches)
print(f"\nMatches for Team {team_id} at Event {event_code}")
print(df_results)

# 7. Save to a clean PDF table
fig, ax = plt.subplots(figsize=(8, 0.3 * len(df_results)))  # Height based on rows
ax.axis('off')

# Create the table
tbl = pd_table(ax, df_results, loc='center', cellLoc='center', colWidths=[0.3]*len(df_results.columns))
tbl.auto_set_font_size(False)
tbl.set_fontsize(10)

# Style the header
for key, cell in tbl.get_celld().items():
    if key[0] == 0:
        cell.set_text_props(weight='bold', color='white')
        cell.set_facecolor('#4C72B0')  # Nice blue
    else:
        cell.set_facecolor('#F5F5F5' if key[0] % 2 == 0 else '#FFFFFF')

# Save to PDF
plt.savefig(f"Team_{team_id}_{event_code}_Matches.pdf", bbox_inches='tight')
print(f"\n✅ PDF saved as: Team_{team_id}_{event_code}_Matches.pdf")
