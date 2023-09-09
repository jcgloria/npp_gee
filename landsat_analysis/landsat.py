import ee
import csv

service_account = 'ucl-676@ee-96juancg.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'ee-96juancg-5fded826f6f1.json')
ee.Initialize(credentials)

def get_dateCount(collection):
    """Function to extract dates from an image collection."""
    return collection.size().getInfo()

# Define the start and end dates.
start_date = '2013-01-01'
end_date = '2018-12-31'

years = list(range(2013, 2019))  # 2013 to 2018

locations = [
    {"name": "Sundarbans", "lat": 21.9497, "lon": 89.1833},
    {"name": "Everglades", "lat": 25.2867, "lon": -80.8987},
    {"name": "Cairns", "lat": -16.9386, "lon": 145.8481},
    {"name": "Can Gio", "lat": 10.4807, "lon": 106.8672}
]

# Prepare to write to CSV
with open('landsat_available_dates.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Location", "Available Dates in 2013-2018"])
    
    for location in locations:
        print(location['name'])
        # Create a point for the given lat, lon
        point = ee.Geometry.Point([location['lon'], location['lat']]).buffer(10000)
        for year in years: 
            # Fetch the Landsat 8 collection for 2021, filtered by the point.
            collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate(str(year) + '-01-01', str(year) + '-12-31').filterBounds(point))
            # Get the dates from the collection.
            available_dates = get_dateCount(collection)
        
            # Write to CSV
            csvwriter.writerow([location['name'],year,available_dates])
