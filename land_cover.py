import ee
import json
import csv

service_account = 'ucl-676@ee-96juancg.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'ee-96juancg-5fded826f6f1.json')
ee.Initialize(credentials)

inputData = json.loads(open('inputData.json', 'r').read())

locations = inputData['locations']

startDate = ee.Date.fromYMD(inputData['year_start'], 1, 1)
# one year later
endDate = ee.Date.fromYMD(inputData['year_end'], 12, 31)

result_data = []

classifications = ["0", "20", "30", "40", "50", "60", "70", "80", "90", "100", "111", "112", "113", "114", "115", "116", "121", "122", "123", "124", "125", "126", "200"]
def calc_metrics(image):
    pixelArea = ee.Image.pixelArea()
    histogram = image.reduceRegion(ee.Reducer.frequencyHistogram(), area, 1000).get('discrete_classification')
    return image.set(histogram).set('area', pixelArea)

for loc in locations:
    area = ee.Geometry.Point(loc['lon'], loc['lat']).buffer(10000)
    col = ee.ImageCollection('COPERNICUS/Landcover/100m/Proba-V-C3/Global').filterDate(startDate, endDate).filterBounds(area)
    result_col = col.map(calc_metrics)
    # Loop through keys and values in properties
    for year in range(inputData['year_start'], inputData['year_end']+1):
        currentImage = result_col.filterDate(ee.Date.fromYMD(year, 1, 1), ee.Date.fromYMD(year, 12, 31)).first()
        properties = currentImage.getInfo()['properties']
        pixelArea = properties['area']
        print(f'Pixel area: {pixelArea} for location {loc["name"]} in year {year}')
        for key, value in properties.items():
            if key in classifications:
                result_data.append({
                    'location': loc['name'],
                    'classification': key,
                    'value': value,
                    'year': year
                })

csv_filename = "land_cover.csv"
with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = ["location", "classification", "value", "year"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in result_data:
        writer.writerow(row)