from bs4 import BeautifulSoup
import requests
import pandas as pd
year_list = []

for year in range(1990, 2022):
    formatted_year = f"{year}-{year+1}"
    year_list.append(formatted_year)

year_list.append('')

base_url = 'https://hoopshype.com/salaries/players/'

for year in year_list:
    players = []
    salaries = []
    url = base_url + year
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')[1:]
    for row in rows:
        cols = row.find_all('td')
        players.append(' '.join(cols[1].text.split()))
        salaries.append(' '.join(cols[2].text.split()))

    data = {
        'player': players,
        'salary': salaries,
    }
    
    final_df = pd.DataFrame(data)
    if year == '':
        year = '2022-2023'
    final_df.to_csv('../0_datasets/salaries/players_slaries_' + year + '.csv',index = False)