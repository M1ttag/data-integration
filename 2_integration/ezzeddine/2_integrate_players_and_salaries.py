import os
import pandas as pd
import uuid

salaries_2019_2020 = pd.read_csv('../../0_datasets/salaries/players_slaries_2019-2020.csv') 
salaries_2020_2021 = pd.read_csv('../../0_datasets/salaries/players_slaries_2020-2021.csv')
salaries_2021_2022 = pd.read_csv('../../0_datasets/salaries/players_slaries_2021-2022.csv') 
salaries_2022_2023 = pd.read_csv('../../0_datasets/salaries/players_slaries_2022-2023.csv')
players = pd.read_csv('../../0_datasets/processed/unique_players.csv')


def process_dataframe(df):
    # Rename "salary" column to "salary_in_usd"
    df.rename(columns={'salary': 'salary_in_usd'}, inplace=True)

    # Convert values in "salary_in_usd" column from string to float
    df['salary_in_usd'] = df['salary_in_usd'].str.replace(',', '').str.replace('$', '').astype(float)

    # Add "uuid" column as the first column with UUID values
    df.insert(0, 'uuid', [str(uuid.uuid4()) for _ in range(len(df))])

    return df

def damerau_levenshtein_distance(s1, s2):
    len1, len2 = len(s1), len(s2)
    d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    
    for i in range(len1 + 1):
        d[i][0] = i
    
    for j in range(len2 + 1):
        d[0][j] = j
    
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,  # deletion
                d[i][j - 1] + 1,  # insertion
                d[i - 1][j - 1] + cost  # substitution
            )
            
            if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)  # transposition
    
    return d[len1][len2]

def integrate_players_salaries(salary_df, uuid_df, threshold = 0):
    salary_df.insert(1, "player_uuid", '')
    for i, row in salary_df.iterrows():
        player_name = row['player']
        min_distance = float('inf')
        matching_uuid = None

        for _, uuid_row in uuid_df.iterrows():
            uuid_name = uuid_row['NAME']
            distance = damerau_levenshtein_distance(player_name, uuid_name)

            if distance < min_distance:
                min_distance = distance
                matching_uuid = uuid_row['uuid']

            if min_distance == threshold:
                break

        if min_distance == threshold:
            salary_df.loc[i, 'player_uuid'] = matching_uuid

    salary_df.drop('player', axis=1, inplace=True)
    return salary_df

# Generate unique UUID for each salary and convert salary to float
salaries_2019_2020 = process_dataframe(salaries_2019_2020)
salaries_2020_2021 = process_dataframe(salaries_2020_2021)
salaries_2021_2022 = process_dataframe(salaries_2021_2022)
salaries_2022_2023 = process_dataframe(salaries_2022_2023)

# Integrate players and salaries
salaries_2019_2020 = integrate_players_salaries(salaries_2019_2020, players)
salaries_2020_2021 = integrate_players_salaries(salaries_2020_2021, players)
salaries_2021_2022 = integrate_players_salaries(salaries_2021_2022, players)
salaries_2022_2023 = integrate_players_salaries(salaries_2022_2023, players)

#Create directory if it doesn't exist
if not os.path.exists('../../0_datasets/processed/salaries'):
    os.makedirs('../../0_datasets/processed/salaries')


# Save integrated salaries
salaries_2019_2020.to_csv('../../0_datasets/processed/salaries/salaries_2019_2020.csv', index=False)
salaries_2020_2021.to_csv('../../0_datasets/processed/salaries/salaries_2020_2021.csv', index=False)
salaries_2021_2022.to_csv('../../0_datasets/processed/salaries/salaries_2021_2022.csv', index=False)
salaries_2022_2023.to_csv('../../0_datasets/processed/salaries/salaries_2022_2023.csv', index=False)