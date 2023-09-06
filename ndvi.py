import ee
import json
import datetime

service_account = 'ucl-676@ee-96juancg.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'ee-96juancg-5fded826f6f1.json')
ee.Initialize(credentials)

def aggregate_monthly_NDVI(year_month):
    year, month = year_month
    start_date = ee.Date.fromYMD(year, month, 1)
    end_date = start_date.advance(1, 'month')

    # Calculate monthly mean
    filtered = collection.filterDate(start_date, end_date)
    monthly_mean = filtered.select('NDVI').mean().rename('monthly_NDVI')

    return monthly_mean.set({
        'system:time_start': start_date.millis(),
        'median': monthly_mean.reduceRegion(ee.Reducer.median(), geometry=area, scale=500).get('monthly_NDVI') # for debugging purposes
    })

def addNDVI(image):
    ndvi = image.normalizedDifference(['sur_refl_b02', 'sur_refl_b01']).rename('NDVI')
    return image.addBands(ndvi)

def print_sample():
    medians = []
    # get some sample data from the first collection.
    for i,col in enumerate(collections):
        dates = col.aggregate_array('system:time_start').map(lambda millis: ee.Date(millis).format('YYYY-MM-dd')).getInfo()
        medians = col.aggregate_array('median').getInfo()
        print('Collection ' + str(i))
        for date, median in zip(dates, medians):
            print(f"Date: {date}, Median: {median}")
            medians.append(median)
    
    print("-------------------")
    print(sum(medians)/len(medians))

def convertToReadable(timestamp):
    return datetime.datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d')

def get_collection(name):
    for collection in collections:
        col_name = collection.get('name').getInfo()
        if col_name == name:
            return collection

##################################
############## MAIN ##############
##################################

inputData = json.loads(open('inputData.json', 'r').read())

locations = inputData['locations']
collections = []

year_start = inputData['year_start']
year_end = inputData['year_end']

for location in locations:
    area = ee.Geometry.Point(location['lon'], location['lat']).buffer(10000) # 10,000m radius
    collection = ee.ImageCollection('MODIS/061/MOD09A1').filterDate(ee.Date.fromYMD(year_start, 1,1), ee.Date.fromYMD(year_end, 12,31)).filterBounds(area)
    
    collection = collection.map(addNDVI)
    
    # Monthly aggregation
    years = list(range(year_start, year_end + 1)) # inclusive
    months = list(range(1, 13)) # 1 to 12
    year_month_pairs = [(y, m) for y in years for m in months]
    
    monthly_images = [aggregate_monthly_NDVI(ym) for ym in year_month_pairs]
    monthly_NDVI_collection = ee.ImageCollection(monthly_images)
    monthly_NDVI_collection = monthly_NDVI_collection.set({'name': location['name']})
    
    collections.append(monthly_NDVI_collection)