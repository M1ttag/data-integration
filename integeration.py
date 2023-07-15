import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from scipy.optimize import curve_fit
from glob import glob
import statsmodels.formula.api as smf
# Load player information
players = pd.read_csv('unique_players.csv')

# Load championship information
champs = pd.read_csv('champions_with_team_ids.csv')

# Load statistics
stats_files = glob('stats.csv')
stats = pd.concat((pd.read_csv(file) for file in stats_files))

# Load salaries
salary_files = glob('salaries.csv')
salaries = pd.concat((pd.read_csv(file) for file in salary_files))

# Load teams information
teams = pd.read_csv('teams_with_uuid.csv')
# Merge dataframes
merged = pd.merge(salaries, stats, on='player_uuid')
merged = pd.merge(merged, players, left_on='player_uuid', right_on='uuid')
performance_metrics = ['RANK', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'USG%', 'TO%', 'eFG%', 'TS%']
correlations = merged[['salary_in_usd'] + performance_metrics].corr()
print(correlations)

# Merge data frames
data = pd.merge(players, salaries, left_on='uuid', right_on='player_uuid')
data = pd.merge(data, stats, on='player_uuid')

# Check for outliers
data.boxplot(column='salary_in_usd')
plt.title('Boxplot of Salaries')
plt.show()

# Convert POS variable to dummy variables
pos_dummies = pd.get_dummies(data['POS'], prefix='POS')

# Add dummy variables to the data frame
data = pd.concat([data, pos_dummies], axis=1)

# Select variables for analysis
variables = ['salary_in_usd', 'AGE', 'USG%', 'eFG%', 'TS%', 'PPG', 'RPG', 'APG'] + list(pos_dummies.columns)

# Calculate correlations
correlations = data[variables].corr()

# Print correlations
print(correlations)

# Visualize correlations
plt.figure(figsize=(10, 10))
sns.heatmap(correlations, annot=True)
plt.show()

# Calculate average salary for each position
average_salary_by_pos = data.groupby('POS')['salary_in_usd'].mean()

# Print results
print(average_salary_by_pos)

# Visualize results
average_salary_by_pos.plot(kind='bar')
plt.title('Average Salary by Position')
plt.xlabel('Position')
plt.ylabel('Average Salary')
plt.show()

# Convert season_x variable to date format
data['season_x'] = data['season_x'].apply(lambda x: x.split('-')[0])

# Calculate average salary for each season
average_salary_by_season = data.groupby('season_x')['salary_in_usd'].mean()

# Print results
print(average_salary_by_season)

# Visualize results
average_salary_by_season.plot()
plt.title('Average Salary by Season')
plt.xlabel('Season')
plt.ylabel('Average Salary')
plt.show()

# Define model function
def model_func(x, a0, a1, a2, a3, a4, a5, a6, b1, b2, b3, b4, c, k):
    is_F, is_GF, is_G, is_C, is_CF, is_FG, is_FC, ppg, rpg, apg, age, season = x
    return (a0 * is_F + a1 * is_GF + a2 * is_G + a3 * is_C + a4 * is_CF + a5 * is_FG + a6 * is_FC) * (b1 * ppg + b2 * rpg + b3 * apg + b4 * age + c) * k ** (season - 2018)

# Encode position variables using one-hot encoding
pos_dummies = pd.get_dummies(data['POS'], prefix='is')

# Add one-hot encoded variables to the data frame
data = pd.concat([data, pos_dummies], axis=1)

# Create explanatory variables and response variable
X = data[['is_F', 'is_G-F', 'is_G', 'is_C', 'is_C-F', 'is_F-G', 'is_F-C', 'PPG', 'RPG', 'APG', 'AGE', 'season_x']].values.T
y = data['salary_in_usd'].values

# Fit the model
popt, pcov = curve_fit(model_func, X, y)

# Print model parameters
print('Coefficients: ', popt)
