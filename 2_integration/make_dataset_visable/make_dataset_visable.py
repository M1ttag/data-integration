# Import pandas library
import pandas as pd

# Read the dataset
df = pd.read_csv(r"D:\data-integration\four_years_data.csv")

# Define a function to calculate the total number of championships for each player based on their four-year teams
def get_championships(row):
    # The Western champions for 2019-2022
    Wchampion_teams = ["Gol", "Los", "Pho","Gol"]
    # The Eastern champions for 2019-2022
    Echampion_teams = ["Ste", "Fra", "Mon","Ste"]
    # Initialize the total number of championships as 0
    total = 0
    # Loop through the player's four-year teams
    for i, team in enumerate([row["2019team"], row["2020team"], row["2021team"], row["2022team"]]):
        # If the team is one of the Western or Eastern champions, increase the total number of championships by 1
        if team in [Wchampion_teams[i], Echampion_teams[i]]:
            total += 1
    # Return the total number of championships
    return total

# Apply the function to each row of the dataset and create a new column
df["total_championships"] = df.apply(get_championships, axis=1)

# Import matplotlib library
import matplotlib.pyplot as plt

# Define a color dictionary to map different colors based on the total_championships value
colors = {0: "red", 1: "blue", 2: "green", 3: "yellow", 4: "purple"}

# Define a year list
years = ["2019", "2020", "2021", "2022"]

# Create a 2x2 image layout
fig, axes = plt.subplots(2, 2)

# Loop through the four years
for i, year in enumerate(years):
    # Calculate the row and column index of the subplot
    row = i // 2
    col = i % 2
    # Plot a scatter plot with rank as x-axis, salary as y-axis, and color as total_championships corresponding color
    axes[row][col].scatter(df[year + "rank"], df[year + "salary"], c=df["total_championships"].map(colors))
    # Add title and axis labels for the subplot
    axes[row][col].set_title("Salary vs Rank for NBA Players (" + year + ")")
    axes[row][col].set_xlabel("Rank")
    axes[row][col].set_ylabel("Salary")

# Adjust the spacing between subplots
plt.tight_layout()

# Show the image
plt.show()
# Create a new image layout
fig, ax = plt.subplots()

# Loop through the four years
for year in years:
    # Plot a scatter plot with rank as x-axis, salary as y-axis, color as total_championships corresponding color, and transparency as 0.5 (to see overlapping points)
    ax.scatter(df[year + "rank"], df[year + "salary"], c=df["total_championships"].map(colors), alpha=0.5)

# Add title and axis labels for the image
ax.set_title("Salary vs Rank for NBA Players (2019-2022)")
ax.set_xlabel("Rank")
ax.set_ylabel("Salary")

# Show the image
plt.show()
