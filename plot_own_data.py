import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("npp_own_data_monthly.csv")

# Filter data for years 2014 to 2018
df = df[df['year'].isin(range(2014, 2019))]

# Get all unique locations
locations = df['location'].unique()

# For each year, plot a graph
for year in range(2014, 2019):
    plt.figure(figsize=(10, 6))
    
    # Filter data for the current year
    yearly_data = df[df['year'] == year]
    
    for location in locations:
        subset = yearly_data[yearly_data['location'] == location]
        plt.plot(subset['month'], subset['npp'], label=location)
    
    # Decorate the plot
    plt.title(f'Mean Monthly NPP for {year}')
    plt.xlabel('Month')
    plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.ylabel('Mean NPP Value (gC/m2/month)')
    plt.legend(loc="best")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.tight_layout()
    
    # Show the plot
    plt.show()