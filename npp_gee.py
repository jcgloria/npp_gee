import ee
import csv
import json

service_account = 'ucl-676@ee-96juancg.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'ee-96juancg-5fded826f6f1.json')
ee.Initialize(credentials)

# Sundarbans, Bangladesh and India:
# Latitude: 21.9497° N
# Longitude: 89.1833° E

# Everglades National Park, Florida, USA:
# Latitude: 25.2867° N
# Longitude: 80.8987° W

# Cairns, Queensland, Australia:
# Latitude: -16.9386° S
# Longitude: 145.8481° E

# Can Gio Biosphere Reserve, Vietnam:
# Latitude: 10.4807° N
# Longitude: 106.8672° E

collection_id = 'MODIS/061/MOD17A3HGF'

inputData = json.loads(open('inputData.json', 'r').read())
year_start = inputData["year_start"]
year_end = inputData["year_end"]
locations = inputData["locations"]

def compute_npp_values(image):
    mean_npp = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=area, scale=500).get('Npp') # get in grams (scale is 0.0001 for kg, so multiply by 0.1)
    total_carbon = image.multiply(image.pixelArea()).reduceRegion(reducer=ee.Reducer.sum(), geometry=area, scale=500).get('Npp') # get in kg (scale is 0.0001 for kg)
    return ee.Feature(None, {"mean_npp": mean_npp, "total_carbon": total_carbon, "year": image.date().get('year').format(), "location": location['name']})

all_data = []
# Loop through years and locations
for location in locations:
    print(f"Processing location {location['name']}")
    area = ee.Geometry.Point(location["lon"], location["lat"]).buffer(10000)
    col = ee.ImageCollection(collection_id).filterDate(ee.Date.fromYMD(year_start, 1,1), ee.Date.fromYMD(year_end, 12,31)).filterBounds(area)
    results = col.map(compute_npp_values).getInfo()
    all_data.extend([feat['properties'] for feat in results['features']])
    # Adjust the values in the all_data list

for data in all_data:
    data['mean_npp'] *= 0.1
    data['total_carbon'] *= 0.0001

# Save the NPP data to a CSV file
csv_filename = "npp_gee_data.csv"
with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = ["year", "location", "mean_npp", "total_carbon"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for data in all_data:
        writer.writerow(data)

print(f"NPP data saved to {csv_filename}")