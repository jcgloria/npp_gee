import ee
import json
import csv
import datetime

service_account = 'ucl-676@ee-96juancg.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'ee-96juancg-5fded826f6f1.json')
ee.Initialize(credentials)

inputData = json.loads(open('inputData.json', 'r').read())

year_start = inputData['year_start']
year_end = inputData['year_end']

def aggregate_monthly_FPAR(year_month):
    year, month = year_month
    start_date = ee.Date.fromYMD(year, month, 1)
    end_date = start_date.advance(1, 'month')

    # Calculate monthly mean
    filtered = mod15_collection.filterDate(start_date, end_date)
    monthly_mean = filtered.select('Fpar_500m').mean().rename('monthly_FPAR')

    return monthly_mean.set({
        'system:time_start': start_date.millis(),
        'mean': monthly_mean.reduceRegion(ee.Reducer.mean(), geometry=area, scale=500).get('monthly_FPAR') # for debugging purposes
    })

collections = []

for loc in inputData['locations']:
    area = ee.Geometry.Point(loc['lon'], loc['lat']).buffer(10000)
    mod15_collection = ee.ImageCollection('MODIS/061/MOD15A2H').filterDate(ee.Date.fromYMD(year_start, 1, 1), ee.Date.fromYMD(year_end, 12, 31)).filterBounds(area)
    # Monthly aggregation
    years = list(range(year_start, year_end + 1)) # inclusive
    months = list(range(1, 13)) # 1 to 12
    year_month_pairs = [(y, m) for y in years for m in months]
    monthly_images = [aggregate_monthly_FPAR(ym) for ym in year_month_pairs]
    monthly_NDVI_collection = ee.ImageCollection(monthly_images)
    monthly_NDVI_collection = monthly_NDVI_collection.set({'name': loc['name']})
    collections.append(monthly_NDVI_collection)

# Save FPAR from MOD15
csv_filename = "mod15_par.csv"
with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = ["name","year", "month", "fpar"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for col in collections:
        data = col.getInfo()
        name = data['properties']['name']
        for img in data['features']:
            date = datetime.datetime.fromtimestamp(img['properties']['system:time_start'] / 1000)
            year = date.year
            month = date.month
            fpar = img['properties']['mean'] * 0.01
            writer.writerow({"name": name, "year": year, "month": month, "fpar": fpar})