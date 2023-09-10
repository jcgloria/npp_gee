import pandas as pd
import matplotlib.pyplot as plt
# 1. Load the CSVs

# Load the NPP data
npp_data_full = pd.read_csv('merged_npp_own_gee_yearly.csv')

# Load the major biome classifications
biome_data_full = pd.read_csv('land_cover.csv')

# 2. Data Preparation

# Rename the 'Area' column for merging purposes
npp_data_full.rename(columns={'Area': 'location'}, inplace=True)

# Compute the NPP difference
npp_data_full['npp_difference'] = npp_data_full['npp_own'] - npp_data_full['npp_gee']

# Filter the biome data to get major biome classifications and pivot it to get a wider format
major_biomes_full = biome_data_full.pivot(index=['year', 'location'], columns='classification', values='value').reset_index()

# Merge NPP data with biome data
merged_data_full = pd.merge(npp_data_full, major_biomes_full, on=['year', 'location'])

# Filter data for Can Gio and Sundarbans
selected_data_full = merged_data_full[merged_data_full['location'].isin(['Can Gio', 'Sundarbans'])]

# 3. Visualization

plt.figure(figsize=(15, 10))

biome_cols_full = biome_data_full['classification'].unique()

for index, location in enumerate(['Can Gio', 'Sundarbans'], 1):
    plt.subplot(2, 1, index)
    
    # Plot NPP difference
    selected_data_full[selected_data_full['location'] == location].plot(x='year', y='npp_difference', ax=plt.gca(), marker='o', color='black', label='NPP Difference (own - gee)', linestyle='-')
    
    # Overlay plots for major biome classifications
    for biome_col in biome_cols_full:
        selected_data_full[selected_data_full['location'] == location].plot(x='year', y=biome_col, ax=plt.gca(), marker='.', label=biome_col)
    
    plt.title(f"NPP Difference & Major Biome Percentages in {location} (2015-2019)")
    plt.ylabel('Value')
    plt.xlabel('Year')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend()

plt.tight_layout()
plt.show()
