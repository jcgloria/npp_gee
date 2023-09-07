import pandas as pd
import matplotlib.pyplot as plt

colors = plt.cm.tab10.colors
df_npp = pd.read_csv("npp_own_data_monthly.csv")
plt.figure(figsize=(15, 8))

# Looping over unique locations and plotting monthly npp data for each location with vibrant colors
for idx, location in enumerate(df_npp['location'].unique()):
    subset = df_npp[df_npp['location'] == location]
    plt.plot(subset['year'] + (subset['month'] - 1) / 12, subset['npp'], label=location, color=colors[idx])

plt.xlabel('Year')
plt.ylabel('NPP (gC/m^2/month))')
plt.title('Monthly NPP data over the years by location')
plt.xticks(list(range(df_npp['year'].min(), df_npp['year'].max() + 1)))  # Set x-ticks to be the unique years in the dataset
plt.legend()
plt.grid(True)
plt.show()
