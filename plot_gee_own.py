import pandas as pd
import matplotlib.pyplot as plt

# Load data
df_gee = pd.read_csv("npp_gee_data.csv")  # columns: year,location,npp,total_carbon

df_own = pd.read_csv("npp_own_data_monthly.csv")  # columns: year,month,location,npp, total_carbon

df_own = df_own.groupby(['year', 'location']).npp.sum().reset_index()

# Merge the two dataframes
merged_df = pd.merge(df_gee[['year', 'location', 'npp']], df_own[['year', 'location', 'npp']], on=['year', 'location'], how='inner', suffixes=('_gee', '_own'))

# Filter data for years 2014 to 2018
merged_df = merged_df[merged_df['year'].isin(range(2014, 2019))]

# Get all unique locations
locations = merged_df['location'].unique()

# Create a color map for each location. Here we're using a predefined set of colors. If you have more locations than colors, consider using a colormap.
colors = ['red', 'blue', 'green', 'orange']
color_map = dict(zip(locations, colors))

# Set up the plot outside the loop
plt.figure(figsize=(12, 8))

# For each location, plot the data using its assigned color
for location in locations:
    print(f'Plotting data for {location}')
    # Filter data for the current location
    subset = merged_df[merged_df['location'] == location]
    
    color = color_map[location]
    plt.plot(subset['year'], subset['npp_gee'], linestyle='--', color=color, label=f'{location} (GEE)')
    plt.plot(subset['year'], subset['npp_own'], color=color, label=f'{location} (Own)')

# Decorate the plot
plt.title(f'Yearly NPP (2014-2018)')
plt.xlabel('Year')
plt.ylabel('NPP Value')
plt.legend(loc="best", ncol=2)  # Setting ncol to 2 for better legend layout
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.tight_layout()

# Explicitly set the x-ticks to be integers
plt.xticks([year for year in range(2014, 2019)])  # Years from 2014 to 2018 inclusive

# Show the plot after the loop
plt.show()
