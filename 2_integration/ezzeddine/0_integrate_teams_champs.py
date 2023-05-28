import pandas as pd
import uuid
import os

def levenshtein_distance(str1, str2):
    """
    Calculate the Levenshtein distance between two strings.
    """
    # Initialize a matrix with dimensions (len(str1) + 1) x (len(str2) + 1)
    matrix = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]

    # Populate the first row and column of the matrix
    for i in range(len(str1) + 1):
        matrix[i][0] = i
    for j in range(len(str2) + 1):
        matrix[0][j] = j

    # Calculate the minimum cost for each cell in the matrix
    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            matrix[i][j] = min(
                matrix[i - 1][j] + 1,           # deletion
                matrix[i][j - 1] + 1,           # insertion
                matrix[i - 1][j - 1] + cost     # substitution
            )

    # Return the value in the bottom-right cell of the matrix (Levenshtein distance)
    return matrix[-1][-1]


# Read the data
teams = pd.read_csv('../../0_datasets/teams.csv')
titles = pd.read_csv('../../0_datasets/teams_won_titles.csv')

# Assign a unique identifier to each team
teams.insert(0, 'uuid', [uuid.uuid4() for _ in range(len(teams))])


# Split the champions data 
western_champs = []
western_champs_years = []
eastern_champs = []
eastern_champs_years = []
for index, row in titles.iterrows():
    row['year'] = row['year'][:4]
    if row['western_champ'].split("(")[0].strip() in teams['name'].values:
        western_champs.append(row['western_champ'])
        western_champs_years.append(row['year'])
    if row['eastern_champ'].split("(")[0].strip() in teams['name'].values:
        eastern_champs.append(row['eastern_champ'])
        eastern_champs_years.append(row['year'])
        
champions_data = {
    'uuid': [uuid.uuid4() for _ in range(len(western_champs) + len(eastern_champs))],
    'year': western_champs_years + eastern_champs_years,
    'region': ['western'] * len(western_champs) + ['eastern'] * len(eastern_champs),
    'champion': western_champs + eastern_champs
}

# Create a DataFrame from the dictionary
champtions = pd.DataFrame(champions_data)

### Integration
# Create an empty list to store the team IDs
team_ids = []

# Iterate through the champions DataFrame
for index, champion_row in champtions.iterrows():
    champion_name = champion_row['champion']
    lowest_distance = float('inf')  # Initialize with a large value
    best_match_id = None

    # Iterate through the teams DataFrame to calculate the Levenshtein distance
    for team_index, team_row in teams.iterrows():
        team_name = team_row['name']
        distance = levenshtein_distance(champion_name, team_name)

        if distance < lowest_distance:
            lowest_distance = distance
            best_match_id = team_row['uuid']

    # Append the team ID to the list
    team_ids.append(best_match_id)

# Add the team ID column to the champions DataFrame
champtions['champion_uuid'] = team_ids

# Save the updated DataFrame to a new CSV file
# champions_df.to_csv('champions_with_team_ids.csv', index=False)
champtions = champtions.drop('champion', axis=1)

directory = "../../0_datasets/processed"
# Create the directory if it doesn't exist
os.makedirs(directory, exist_ok=True)

# Save the updated DataFrame to a new CSV file
champtions.to_csv('../../0_datasets/processed/champions_with_team_ids.csv', index=False)
teams.to_csv('../../0_datasets/processed/teams_with_uuid.csv', index=False)