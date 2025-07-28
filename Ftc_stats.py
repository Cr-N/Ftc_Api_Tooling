import pandas as pd
import requests

year = input("Enter year: ")
team_id = input("Enter team id: ")

url = f"https://api.ftcscout.org/rest/v1/teams/{team_id}/events/{year}"

response = requests.get(url)
data = response.json()

df = pd.DataFrame(data)
df = pd.json_normalize(data)

excel = "TeamStats.xlsx"
df.to_excel(excel, index=False)
