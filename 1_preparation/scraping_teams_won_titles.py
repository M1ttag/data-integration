from bs4 import BeautifulSoup
import requests
import pandas as pd

url = 'https://en.wikipedia.org/wiki/List_of_NBA_champions'
req = requests.get(url)
soup = BeautifulSoup(req.content, 'html.parser')

table = soup.find_all("table", {"class": "wikitable"})[1]
table = table.find_all("tbody")[0]
rows = table.find_all("tr")[1:][1:]

year = []
western_champ = []
western_coach = []
score = []
eastern_champ = []
eastern_coach = []

for row in rows:
    cols = row.find_all('td')
    if len(cols) > 1:
        year.append(cols[0].text)
        western_champ.append(cols[1].text)
        western_coach.append(cols[2].text)
        score.append(cols[3].text)
        eastern_champ.append(cols[4].text)
        eastern_coach.append(cols[5].text)

data = {
    'year': year,
    'western_champ': western_champ,
    'western_coach': western_coach,
    'score': score,
    'eastern_champ': eastern_champ,
    'eastern_coach': eastern_coach,
}

final_df = pd.DataFrame(data)
final_df.to_csv('../0_datasets/teams_won_titles.csv',index = False)