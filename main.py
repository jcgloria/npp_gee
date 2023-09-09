import ee
import ndvi
import lue
import par
import json
import csv

service_account = 'ucl-676@ee-96juancg.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'ee-96juancg-5fded826f6f1.json')
ee.Initialize(credentials)

def get_image_by_date(collection, date):
    return ee.Image(collection.filterDate(date, date.advance(1, 'day')).first())

def multiply_bands(image):
    date = image.date()
    par_image = get_image_by_date(par_collection, date)
    lue_image = get_image_by_date(lue_collection, date)
    if not (par_image or lue_image):
        print(f"Could not find PAR or LUE image for {date}")

    result = image.select('monthly_NDVI').multiply(par_image.select('monthly_PAR')).multiply(lue_image.select('LUE')).rename('NPP')

    mean = result.reduceRegion(reducer=ee.Reducer.mean(), geometry=area, scale=500).get('NPP')
    total_carbon_image = result.multiply(image.pixelArea())
    total_carbon = total_carbon_image.reduceRegion(reducer=ee.Reducer.sum(), geometry=area, scale=500).get('NPP')

    return result.set({'system:time_start': date.millis(), 'mean_NPP': mean, 'total_carbon': total_carbon})

def saveImage(image, year, month, locName):
    print(f"Saving image for {year}-{month} in {locName}")
    locName = locName.replace(' ', '_')
    task = ee.batch.Export.image.toAsset(image=image,assetId='projects/ee-96juancg/assets/'+'npp_'+locName +'_'+str(year)+"_"+str(month), description='npp_'+locName+'_'+str(year),scale=500,region=area)
    task.start()

inputData = json.loads(open('inputData.json').read())
locations = inputData['locations']

npp_data = []

yearRange = list(range(inputData['year_start'], inputData['year_end'] + 1))
for loc in locations:
    area = ee.Geometry.Point(loc['lon'], loc['lat']).buffer(10000)
    for year in yearRange:
        ndvi_collection = ndvi.get_collection(loc['name']).filterDate(ee.Date.fromYMD(year, 1, 1), ee.Date.fromYMD(year, 12, 31))
        par_collection = par.get_collection(loc['name'])
        lue_collection = lue.get_collection(loc['name'])
        result_collection = ndvi_collection.map(multiply_bands) # Use NDVI collection as a base
        monthly_npp = result_collection.aggregate_array('mean_NPP').getInfo() 
        monthly_carbon = result_collection.aggregate_array('total_carbon').getInfo() 
        
        for i in range(0, len(monthly_npp)):
            npp_data.append({"year": year, "month": i + 1, "location": loc['name'], "npp": monthly_npp[i], "carbon": monthly_carbon[i]})
            print(f"Year: {year}, Month: {i + 1}, Location: {loc['name']}, NPP: {monthly_npp[i]}, Carbon: {monthly_carbon[i]}")
            saveImage(result_collection.filterDate(ee.Date.fromYMD(year,i+1,1), ee.Date.fromYMD(year,i+1,1).advance(1, 'month')).first(), year, i + 1, loc['name'])
    
# Save the NPP data to a CSV file
csv_filename = "npp_own_data_monthly.csv"
with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = ["year", "month", "location", "npp", "carbon"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for data in npp_data:
        writer.writerow(data)

print(f"NPP data saved to {csv_filename}")