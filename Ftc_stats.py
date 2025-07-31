import pandas as pd
import requests


option = input("1 - All Event Stats for a Team\n"
               "2 - Just Team Stats\n"
               "3 - Show with who did a Team play in a certain Event\n"
               "Enter option: ")

if option == "1":
    team_id = input("Enter team ID: ")
    year = input("Enter year: ")
    url1 = f"https://api.ftcscout.org/rest/v1/teams/{team_id}/events/{year}"
    response = requests.get(url1)

    data = response.json()

    df = pd.DataFrame(data)
    df = pd.json_normalize(data)
    pd.set_option('display.max_columns', None)
    df = df[['stats.avg.totalPoints', 'stats.avg.autoPoints', 'stats.avg.dcPoints', 'stats.rank', 'eventCode']]
    df = df.rename(columns={'stats.avg.totalPoints': 'Total', 'stats.avg.autoPoints': 'Auto Avg', 'stats.avg.dcPoints': 'DC Avg', 'stats.rank': 'Rank', 'eventCode': 'Event'})

    print(df)


if option == "2":
    team_id = input("Enter team ID: ")
    url2 = f"https://api.ftcscout.org/rest/v1/teams/{team_id}/quick-stats"
    response = requests.get(url2)
    data = response.json()

    df = pd.DataFrame(data)
    df = pd.json_normalize(data)

    pd.set_option('display.max_columns', None)
    print(df)

if option == "3":
    team_id = int(input("Enter team ID: "))
    year = input("Enter year: ")
    url4 = f"https://api.ftcscout.org/rest/v1/teams/{team_id}/events/{year}"
    responsee = requests.get(url4)
    data2 = responsee.json()
    dfe = pd.DataFrame(data2)
    dfe = pd.json_normalize(data2)
    dfe = dfe[['eventCode']]
    dfe.rename(columns={'eventCode': 'Event'}, inplace=True)
    print(dfe)

    eventCode = int(input("Enter event code: "))
    url3 = f"https://api.ftcscout.org/rest/v1/events/{year}/{dfe.iloc[eventCode]['Event']}/matches"
    response = requests.get(url3)
    data1 = response.json()

    df = pd.DataFrame(data1)
    df = pd.json_normalize(data1, 'teams')
    df = df[['matchId', 'alliance', 'teamNumber']]
    pd.set_option('display.max_rows', None)
    Matches = df[df['teamNumber'] == team_id]
    alliance = Matches['alliance']
    match_id = Matches['matchId']
    filter = list(zip(match_id, alliance))
    match = df[(df[['matchId', 'alliance']].apply(tuple, axis=1).isin(filter)) & (df['teamNumber'] != team_id)]
    match = match[['teamNumber']]
    Matches.insert(3, "Team_two", match['teamNumber'].values)

    Names = []
    team2 = 0

    for i in range(0, len(match.index)):
        team2 = match.iloc[i]['teamNumber']
        url5 = f"https://api.ftcscout.org/rest/v1/teams/{team2}"
        responseName = requests.get(url5)
        data2 = responseName.json()
        dfN = pd.DataFrame(data2)
        dfN = pd.json_normalize(data2)
        dfN = dfN[['name']]
        Names.append(dfN['name'].tolist())
    Matches.insert(4, "Team_two_name", Names)
    print(Matches)

#excel = "TeamStats.xlsx"
#df.to_excel(excel, index=False)