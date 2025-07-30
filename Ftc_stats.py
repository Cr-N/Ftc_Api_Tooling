import pandas as pd
import requests


option = input("1 - All Event Stats\n"
               "2 - Team Stats\n"
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



#excel = "TeamStats.xlsx"
#df.to_excel(excel, index=False)