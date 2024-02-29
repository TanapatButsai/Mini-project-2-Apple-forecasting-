import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file, assuming it's in the same directory as the Python script
file_path = 'Apple462.csv'  # Adjusted file path
data = pd.read_csv(file_path)

# Convert 'Date' column to datetime format and set it as the index
data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
data.set_index('Date', inplace=True)

# Sort the dataframe by date
data.sort_index(inplace=True)

# Filter data for 'USA' region
data_canada = data[data['region'] == 'Canada']

# Convert 'Envi', 'Fuji', and 'Gala' columns in the filtered dataset to numeric data types
data_canada[['Envi', 'Fuji', 'Gala']] = data_canada[['Envi', 'Fuji', 'Gala']].apply(pd.to_numeric, errors='coerce')

# Interpolate missing values for the 'USA' region dataset
data_usa_interpolated = data_canada[['Envi', 'Fuji', 'Gala']].interpolate()

# Visualize the time series data for 'Envi', 'Fuji', and 'Gala' for the 'USA' region
plt.figure(figsize=(14, 7))
plt.plot(data_usa_interpolated.index, data_usa_interpolated['Envi'], label='Envi', )
plt.plot(data_usa_interpolated.index, data_usa_interpolated['Fuji'], label='Fuji', )
plt.plot(data_usa_interpolated.index, data_usa_interpolated['Gala'], label='Gala', )
plt.title('Time Series of Apple Varieties in the USA (Interpolated)')
plt.xlabel('Date')
plt.ylabel('Quantity/Metric')
plt.legend()
plt.grid(True)
plt.show()
