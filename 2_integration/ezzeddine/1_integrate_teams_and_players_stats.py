import pandas as pd
import uuid
from itertools import zip_longest
from collections import Counter
import os

def rename_columns(df, column_mapping):
    """
    Renames columns in a DataFrame based on the provided mapping.
    Drops columns with an asterisk (*) in the mapping.
    
    Args:
        df (pandas.DataFrame): DataFrame to rename columns.
        column_mapping (dict): Dictionary mapping old column names to new column names.
    
    Returns:
        pandas.DataFrame: DataFrame with renamed columns and dropped columns.
    """
    # Rename columns
    renamed_df = df.rename(columns=column_mapping)
    
    # Drop columns with asterisk (*) in the mapping
    cols_to_drop = [col for col in renamed_df.columns if '*' in col]
    cleaned_df = renamed_df.drop(cols_to_drop, axis=1)
    
    return cleaned_df

def drop_duplicates(df, column):
    """
    Drops duplicate rows based on a specific column in a DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame to drop duplicates from.
        column (str): Name of the column to check for duplicates.
    
    Returns:
        pandas.DataFrame: DataFrame with duplicate rows dropped.
    """
    duplicated = df.duplicated(subset=column, keep=False)
    cleaned_df = df[~duplicated]
    
    return cleaned_df

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

def add_player_uuid(df, uuid_df, threshold=0):
    df.insert(0, "player_uuid", '')
    for i, row in df.iterrows():
        player_name = row['NAME']
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
            df.loc[i, 'player_uuid'] = matching_uuid

    df.drop('NAME', axis=1, inplace=True)
    return df

def add_team_uuid(df, uuid_df, threshold=0):
    df.insert(0, "team_uuid", '')  # Inserting the "team_uuid" column as the first column
    for i, row in df.iterrows():
        team_name = row['TEAM'].lower()
        min_distance = float('inf')
        matching_uuid = None
        
        for _, uuid_row in uuid_df.iterrows():
            uuid_team = uuid_row['prefix_1']
            distance = damerau_levenshtein_distance(team_name, uuid_team)
            
            if distance < min_distance:
                min_distance = distance
                matching_uuid = uuid_row['uuid']
                
            if min_distance == threshold:
                break
        
        if min_distance == threshold:
            df.loc[i, 'team_uuid'] = matching_uuid
            
    df.drop('TEAM', axis=1, inplace=True)
    return df

# Load Data
stats_2019_2020 = pd.read_excel('../../0_datasets/stats/2019-2020 NBA Player Stats.xlsx', skiprows=1) 
stats_2020_2021 = pd.read_excel('../../0_datasets/stats/2020-2021 NBA Stats  Player Box Score  Advanced Metrics.xlsx', skiprows=1)
stats_2021_2022 = pd.read_excel('../../0_datasets/stats/NBA Stats 202122 All Player Statistics in one Page.xlsx', skiprows=1) 
stats_2022_2023 = pd.read_csv('../../0_datasets/stats/NBA Stats 202223 All Stats  NBA Player Props Tool (1).csv')
teams = pd.read_csv('../../0_datasets/processed/teams_with_uuid.csv')

column_mapping = {
    "RANK": "RANK",
    "FULL NAME": "NAME",
    "TEAM": "TEAM",
    "POS": "POS",
    "AGE": "AGE",
    "GP": "GP",
    "MPG": "MPG",
    "MIN%Minutes PercentagePercentage of team minutes used by a player while he was on the floor": "*",
    "USG%Usage RateUsage rate, a.k.a., usage percentage is an estimate of the percentage of team plays used by a player while he was on the floor": "USG%",
    "TO%Turnover RateA metric that estimates the number of turnovers a player commits per 100 possessions": "TO%",
    "FTA": "FTA",
    "FT%": "FT%",
    "2PA": "2PA",
    "2P%": "2P%",
    "3PA": "3PA",
    "3P%": "3P%",
    "eFG%Effective Shooting PercentageWith eFG%, three-point shots made are worth 50% more than two-point shots made. eFG% Formula=(FGM+ (0.5 x 3PM))/FGA": "eFG%",
    "TS%True Shooting PercentageTrue shooting percentage is a measure of shooting efficiency that takes into account field goals, 3-point field goals, and free throws.": "TS%",
    "PPGPointsPoints per game.": "PPG",
    "RPGReboundsRebounds per game.": "RPG",
    "TRB%Total Rebound PercentageTotal rebound percentage is estimated percentage of available rebounds grabbed by the player while the player is on the court.": "*",
    "APGAssistsAssists per game.": "APG",
    "AST%Assist PercentageAssist percentage is an estimated percentage of teammate field goals a player assisted while the player is on the court": "P+A",
    "SPGStealsSteals per game.": "SPG",
    "BPGBlocksBlocks per game.": "BPG",
    "TOPGTurnoversTurnovers per game.": "TPG",
    "VIVersatility IndexVersatility index is a metric that measures a player’s ability to produce in points, assists, and rebounds. The average player will score around a five on the index, while top players score above 10": "VI",
    "ORTGOffensive RatingIndividual offensive rating is the number of points produced by a player per 100 total individual possessions.": "ORtg",
    "DRTGDefensive RatingIndividual defensive rating estimates how many points the player allowed per 100 possessions he individually faced while staying on the court.": "DRtg"
}


# Rename columns in each DataFrame individually
stats_2019_2020 = rename_columns(stats_2019_2020, column_mapping)
stats_2020_2021 = rename_columns(stats_2020_2021, column_mapping)
stats_2021_2022 = rename_columns(stats_2021_2022, column_mapping)

# Drop columns that are not in all DataFrames
stats_2022_2023 = stats_2022_2023.drop('P+R+A', axis=1)
stats_2022_2023 = stats_2022_2023.drop('P+R', axis=1)

# Drop duplicate rows
stats_2019_2020 = drop_duplicates(stats_2019_2020, 'NAME')
stats_2020_2021 = drop_duplicates(stats_2020_2021, 'NAME')
stats_2021_2022 = drop_duplicates(stats_2021_2022, 'NAME')
stats_2022_2023 = drop_duplicates(stats_2022_2023, 'NAME')

# Create a new DataFrame with only the player name column & assign UUIDs
df1_selected = stats_2019_2020[['NAME']]
df2_selected = stats_2020_2021[['NAME']]
df3_selected = stats_2021_2022[['NAME']]
df4_selected = stats_2022_2023[['NAME']]

# Concatenate selected columns from all four DataFrames
merged_df = pd.concat([df1_selected, df2_selected, df3_selected, df4_selected])

# Assign UUIDs to the players
merged_df['uuid'] = [str(uuid.uuid4()) for _ in range(len(merged_df))]

# Drop duplicate rows based on the player name column
unique_players_df = merged_df.drop_duplicates(subset='NAME')
unique_players_df.reset_index()
directory = "../../0_datasets/processed"
# Create the directory if it doesn't exist
os.makedirs(directory, exist_ok=True)
unique_players_df.to_csv('../../0_datasets/processed/unique_players.csv', index=False, columns=['uuid', 'NAME'])

# Integrate players to stats
stats_2019_2020 = add_player_uuid(stats_2019_2020, unique_players_df)
stats_2020_2021 = add_player_uuid(stats_2020_2021, unique_players_df)
stats_2021_2022 = add_player_uuid(stats_2021_2022, unique_players_df)
stats_2022_2023 = add_player_uuid(stats_2022_2023, unique_players_df)


# Integrate teams to stats
stats_2019_2020 = add_team_uuid(stats_2019_2020, teams)
stats_2020_2021 = add_team_uuid(stats_2020_2021, teams)
stats_2021_2022 = add_team_uuid(stats_2021_2022, teams)
stats_2022_2023 = add_team_uuid(stats_2022_2023, teams)

directory = "../../0_datasets/processed/stats"
# Create the directory if it doesn't exist
os.makedirs(directory, exist_ok=True)
stats_2019_2020.to_csv('../../0_datasets/processed/stats/stats_2019_2020.csv', index=False)
stats_2020_2021.to_csv('../../0_datasets/processed/stats/stats_2020_2021.csv', index=False)
stats_2021_2022.to_csv('../../0_datasets/processed/stats/stats_2021_2022.csv', index=False)
stats_2022_2023.to_csv('../../0_datasets/processed/stats/stats_2022_2023.csv', index=False)
