import requests
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import table as pd_table


# === GRAPHQL REQUEST FUNCTION ===
def graphql_query(query: str, variables: dict):
    url = "https://api.ftcscout.org/graphql"
    headers = {"Content-Type": "application/json"}
    payload = {"query": query, "variables": variables}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


# === GET EVENTS FOR TEAM ===
def get_team_events(team_number: int, season: int):
    query = """
    query ($number: Int!, $season: Int!) {
      teamByNumber(number: $number) {
        events(season: $season) {
          eventCode
        }
      }
    }
    """
    variables = {"number": team_number, "season": season}
    data = graphql_query(query, variables)
    return data["data"]["teamByNumber"]["events"]


# === GET MATCHES FOR EVENT ===
def get_event_matches(event_code: str, season: int):
    query = """
    query ($season: Int!, $code: String!) {
      eventByCode(season: $season, code: $code) {
        matches {
          matchNum
          teams {
            teamNumber
            alliance
            team {
              name
            }
          }
        }
      }
    }
    """
    variables = {"season": season, "code": event_code}
    data = graphql_query(query, variables)
    return data["data"]["eventByCode"]["matches"]


# === MAIN SCRIPT ===
def main():
    team_id = int(input("Enter your team ID: "))
    season = int(input("Enter season (e.g., 2024): "))

    # 1. Get all events
    events = get_team_events(team_id, season)
    df_events = pd.DataFrame(events)
    df_events.rename(columns={'eventCode': 'Event'}, inplace=True)

    print("\nAvailable Events:")
    print(df_events)

    # 2. Select an event
    event_index = int(input("Select an event index from above: "))
    event_code = df_events.iloc[event_index]['Event']

    # 3. Get matches
    matches = get_event_matches(event_code, season)

    # 4. Filter relevant matches
    relevant_matches = []

    for match in matches:
        teams = match['teams']
        team_numbers = [t['teamNumber'] for t in teams]

        if team_id not in team_numbers:
            continue

        my_team = next((t for t in teams if t['teamNumber'] == team_id), None)
        if not my_team:
            continue  # skip if something is wrong

        my_alliance = my_team['alliance']
        my_name = my_team['team']['name']

        alliance_teams = [t for t in teams if t['alliance'] == my_alliance]
        opponent_teams = [t for t in teams if t['alliance'] != my_alliance]

        partner = next((t for t in alliance_teams if t['teamNumber'] != team_id), None)
        partner_str = f"{partner['teamNumber']} ({partner['team']['name']})" if partner else "N/A"

        match_entry = {
            'Match': f"Q{match['matchNum']}",
            'Alliance': my_alliance.capitalize(),
            'Your Team': f"{team_id} ({my_name})",
            'Partner': partner_str,
            'Opponent 1': f"{opponent_teams[0]['teamNumber']} ({opponent_teams[0]['team']['name']})",
            'Opponent 2': f"{opponent_teams[1]['teamNumber']} ({opponent_teams[1]['team']['name']})",
        }

        relevant_matches.append(match_entry)

    # 5. Display DataFrame
    df_results = pd.DataFrame(relevant_matches)
    print(f"\nMatches for Team {team_id} at Event {event_code}")
    print(df_results)

    # 6. Save to PDF
    fig, ax = plt.subplots(figsize=(8, 0.3 * len(df_results)))
    ax.axis('off')

    tbl = pd_table(ax, df_results, loc='center', cellLoc='center', colWidths=[0.3] * len(df_results.columns))
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)

    for key, cell in tbl.get_celld().items():
        if key[0] == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#4C72B0')
        else:
            cell.set_facecolor('#F5F5F5' if key[0] % 2 == 0 else '#FFFFFF')

    filename = f"Team_{team_id}_{event_code}_Matches.pdf"
    plt.savefig(filename, bbox_inches='tight')
    print(f"\n✅ PDF saved as: {filename}")


# === RUN ===
if __name__ == "__main__":
    main()
