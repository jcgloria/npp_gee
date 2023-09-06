import pandas as pd
import matplotlib.pyplot as plt

#columns: location, year, available_dates
df = pd.read_csv('landsat_available_dates.csv')

df_pivot = df.pivot(index='Year', columns='Location', values='Available Dates in 2013-2018')
ax = df_pivot.plot(kind='bar', figsize=(10, 7))

# Set the title and labels
ax.set_title('Number of Available Dates in 2013-2018 for Each Location')
ax.set_xlabel('Year')
ax.set_ylabel('Available Dates in 2013-2018')

# Display the legend
ax.legend(title='Location')

# Display the plot
plt.tight_layout()
plt.show()





