import ee
import json
import csv
import datetime

service_account = 'ucl-676@ee-96juancg.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'ee-96juancg-5fded826f6f1.json')
ee.Initialize(credentials)

band_list = ['GMT_0000_PAR', 'GMT_0300_PAR', 'GMT_0600_PAR', 'GMT_0900_PAR', 'GMT_1200_PAR', 'GMT_1500_PAR', 'GMT_1800_PAR', 'GMT_2100_PAR']

def compute_daily_par(image):
    # This will store the trapezoidal sum
    trapezoidal_sum = ee.Image(0)
    
    # For each band in the band list, compute the average with the next band
    # and multiply by the time interval (3 hours in terms of a day = 3/24)
    for i in range(len(band_list) - 1):
        avg_current_next = image.select(band_list[i]).add(image.select(band_list[i+1])).divide(2)
        trapezoidal_sum = trapezoidal_sum.add(avg_current_next.multiply(3/24))

    trapezoidal_sum = trapezoidal_sum.multiply(0.0864) # Convert W/m^2 to MJ/m^2/day
    
    img = image.addBands(trapezoidal_sum.rename('daily_PAR'))
    mean = img.reduceRegion(reducer=ee.Reducer.mean(), geometry=area, scale=500).get('daily_PAR')
    img = img.set('mean', mean)
    return img

def aggregate_monthly_PAR(year_month):
    year, month = year_month
    start_date = ee.Date.fromYMD(year, month, 1)
    end_date = start_date.advance(1, 'month')
    
    # Filter the daily collection for the given month and year
    filtered = daily_collection.filterDate(start_date, end_date)
    
    # Sum the daily PAR values to get the monthly PAR for each pixel
    monthly_sum = filtered.select('daily_PAR').sum().rename('monthly_PAR')

    # get the mean and store it as a property
    mean = monthly_sum.reduceRegion(reducer=ee.Reducer.mean(), geometry=area, scale=500).get('monthly_PAR')

    return monthly_sum.set('system:time_start', start_date.millis()).set('monthly_PAR', mean)

def get_collection(name):
    for collection in collections:
        col_name = collection.get('name').getInfo()
        if col_name == name:
            return collection

##################################
############## MAIN ##############
##################################

inputData = json.loads(open('inputData.json', 'r').read())
collections = []

year_start = inputData['year_start']
year_end = inputData['year_end']

for loc in inputData['locations']:
    point = ee.Geometry.Point([loc['lon'], loc['lat']])
    area = point.buffer(10000)
    # This MODIS product has instant PAR values in 3-hour intervals for each day. 
    collection = (ee.ImageCollection('MODIS/061/MCD18C2').filterDate(ee.Date.fromYMD(year_start, 1,1), ee.Date.fromYMD(year_end, 12,31)).filterBounds(area))

    daily_collection = collection.map(compute_daily_par)

    # get year range from input data
    years = list(range(year_start, year_end + 1)) # inclusive
    months = list(range(1, 13)) # 1 to 12
    year_month_pairs = [(y, m) for y in years for m in months]

    monthly_images = [aggregate_monthly_PAR(ym) for ym in year_month_pairs]
    monthly_collection = ee.ImageCollection(monthly_images)

    monthly_collection = monthly_collection.set({'name': loc['name']})
    collections.append(monthly_collection)

csv_filename = "par.csv"
with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = ["name","year", "month", "par"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for col in collections:
        data = col.getInfo()
        name = data['properties']['name']
        for img in data['features']:
            date = datetime.datetime.fromtimestamp(img['properties']['system:time_start'] / 1000)
            year = date.year
            month = date.month
            par = img['properties']['monthly_PAR'] 
            writer.writerow({"name": name, "year": year, "month": month, "par": par})