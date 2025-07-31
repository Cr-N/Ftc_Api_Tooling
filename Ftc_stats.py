import time
import matplotlib.pyplot as plt
import pandas as pd
import requests

while True:

    option = input("1 - All Event Stats for a Team\n"
                   "2 - Just Team Stats\n"
                   "3 - Show with who did a Team play in a certain Event\n"
                   "4 - Plot scores from events\n"
                   "5 - Compare 2 teams\n"
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
        excel = "TeamStats.xlsx"
        df.to_excel(excel, index=False)
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

    if option == "4":
        team_id = input("Enter team ID: ")
        year = input("Enter year: ")
        url1 = f"https://api.ftcscout.org/rest/v1/teams/{team_id}/events/{year}"
        response = requests.get(url1)
        data = response.json()
        df = pd.DataFrame(data)
        df = pd.json_normalize(data)
        df = df.iloc[::-1]
        df = df[['stats.avg.totalPoints', 'stats.avg.autoPoints', 'stats.avg.dcPoints', 'stats.rank', 'eventCode']]
        df = df.rename(columns={'stats.avg.totalPoints': 'Total', 'stats.avg.autoPoints': 'Auto Avg', 'stats.avg.dcPoints': 'DC Avg', 'stats.rank': 'Rank', 'eventCode': 'Event'})
        plt.plot(df['Event'], df['Total'], label='Total')
        plt.plot(df['Event'], df['Auto Avg'], label='Auto Avg')
        plt.plot(df['Event'], df['DC Avg'], label='DC Avg')
        plt.legend()
        plt.xlabel("Event")
        plt.ylabel("Points")
        plt.show()

    if option == "5":
        team_id = input("Enter team ID: ")
        team_id2 = input("Enter team ID for team 2: ")
        year = input("Enter year: ")
        url1 = f"https://api.ftcscout.org/rest/v1/teams/{team_id}/events/{year}"
        response = requests.get(url1)
        data = response.json()
        df = pd.DataFrame(data)
        df = pd.json_normalize(data)
        #df = df.iloc[::-1]
        df = df[['stats.avg.totalPoints', 'stats.avg.autoPoints', 'stats.avg.dcPoints', 'stats.rank', 'eventCode', 'updatedAt']]
        df = df.rename(columns={'stats.avg.totalPoints': 'Total', 'stats.avg.autoPoints': 'Auto Avg', 'stats.avg.dcPoints': 'DC Avg', 'stats.rank': 'Rank', 'eventCode': 'Event', 'updatedAt': 'Updated'})
        df.sort_values(by=['Updated'], ascending=True, inplace=True, ignore_index=True)

        plt.plot(df.index, df['Total'], label=f'Total {team_id}')
        plt.plot(df.index, df['Auto Avg'], label=f'Auto Avg {team_id}')
        plt.plot(df.index, df['DC Avg'], label=f'DC Avg {team_id}')


        url1_2 = f"https://api.ftcscout.org/rest/v1/teams/{team_id2}/events/{year}"
        response2 = requests.get(url1_2)
        data2 = response2.json()
        df2 = pd.DataFrame(data2)
        df2 = pd.json_normalize(data2)
        #df2 = df2.iloc[::-1]
        df2 = df2[['stats.avg.totalPoints', 'stats.avg.autoPoints', 'stats.avg.dcPoints', 'stats.rank', 'eventCode', 'updatedAt']]
        df2 = df2.rename(columns={'stats.avg.totalPoints': 'Total', 'stats.avg.autoPoints': 'Auto Avg', 'stats.avg.dcPoints': 'DC Avg', 'stats.rank': 'Rank', 'eventCode': 'Event', 'updatedAt': 'Updated'})
        df2.sort_values(by=['Updated'], ascending=True, inplace=True, ignore_index=True)
        
        print(df)
        print(df2)

        plt.plot(df2.index, df2['Total'], linestyle = ':', label=f'Total {team_id2}')
        plt.plot(df2.index, df2['Auto Avg'], linestyle = ':', label=f'Auto Avg {team_id2}')
        plt.plot(df2.index, df2['DC Avg'], linestyle = ':', label=f'DC Avg {team_id2}')

        plt.legend()
        plt.xlabel("Event")
        plt.ylabel("Points")
        plt.show()


    time.sleep(5)

    print('\n\n')


