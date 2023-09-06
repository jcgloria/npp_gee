import ee
import json
import ndvi

service_account = 'ucl-676@ee-96juancg.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'ee-96juancg-5fded826f6f1.json')
ee.Initialize(credentials)

def resample_image(image):
    return image.resample('bilinear').reproject(crs='EPSG:4326', scale=500) # 500m resolution

def calculate_water_stress(image):
    # Calculate the ratio ET/PET
    ratio = image.select('aet').divide(image.select('pet'))

    # Calculate W = 0.5 * ratio
    W = ratio.add(0.5).rename('W')

    # Return the image with the new band added
    return image.addBands(W)

def find_tOpt(image):
    # The tOpt is the mean temperature during the month where the NDVI is highest. 

    # get the year of the current image
    year = ee.Date(image.get('system:time_start')).get('year')
    # find the highest NDVI value in ndvi_collection for that year
    max_ndvi = ndvi_collection.filterDate(ee.Date.fromYMD(year, 1, 1), ee.Date.fromYMD(year, 12, 31)).sort('monthly_NDVI', False).first()
    # get the date of the highest NDVI value
    max_ndvi_date = ee.Date(max_ndvi.get('system:time_start'))
    # get the mean temperature during the month of the highest NDVI value
    t_opt = t_collection_monthly.filterDate(max_ndvi_date, max_ndvi_date.advance(1, 'month')).first().select('mean_2m_air_temperature').subtract(273.15) #convert to C
    return t_opt

def calculate_LUE(image):
    t_opt = find_tOpt(image)
    
    # mean temperature right now
    t = t_collection_monthly.filterMetadata('system:time_start', 'equals', image.date().millis()).first().select('mean_2m_air_temperature').subtract(273.15) # convert to C
    # T_1 calculation
    result_t_1 = t_opt.multiply(0.02).add(0.8).subtract(t_opt.pow(2).multiply(0.0005))
    # T_2 calculation
    t_2_numerator_1 = ee.Image.constant(1.1814)
    t_2_exponent_1 = t_opt.subtract(t).subtract(10).multiply(-0.2) 
    t_2_denominator_1 = ee.Image.constant(1).add(t_2_exponent_1.exp())
    result_t_2_1 = t_2_numerator_1.divide(t_2_denominator_1)
    t_2_exponent_2 = t_opt.add(t).subtract(10).multiply(-0.3)
    t_2_denominator_2 = ee.Image.constant(1).add(t_2_exponent_2.exp())
    result_t_2_2 = ee.Image.constant(1).divide(t_2_denominator_2)
    result_t_2 = result_t_2_1.multiply(result_t_2_2)
    # Make the product a band in the image
    result = result_t_1.multiply(result_t_2).multiply(ee.Image(MAX_E)).multiply(image.select('W')).rename("LUE")
    image = image.set('median', result.reduceRegion(ee.Reducer.median(), geometry=area, scale=500).get('LUE')) # for debugging purposes
    return image.addBands(result)

def print_sample():
    col = collections[0]
    t_opt = col.aggregate_array('t_opt').getInfo()
    t = col.aggregate_array('t').getInfo()
    t1 = col.aggregate_array('t1').getInfo()
    t2 = col.aggregate_array('t2').getInfo()
    dates = col.aggregate_array('system:time_start').map(lambda millis: ee.Date(millis).format('YYYY-MM-dd')).getInfo()
    medians = col.aggregate_array('median').getInfo()
    for i in range(len(t_opt)):
        print(f"Date: {dates[i]}")
        print(f"t_opt: {t_opt[i]}")
        print(f"t: {t[i]}")
        print(f"t1: {t1[i]}")
        print(f"t2: {t2[i]}")
        print(f"median: {medians[i]}")
        print("")

def get_collection(name):
    for collection in collections:
        col_name = collection.get('name').getInfo()
        if col_name == name:
            return collection

inputData = json.loads(open('inputData.json', 'r').read())
collections = []
MAX_E = 2.5

for location in inputData['locations']:
    
    area = ee.Geometry.Point(location['lon'], location['lat']).buffer(10000) # 10,000m radius

    # MOD16A2 (ET and PET)
    et_pet_collection = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').filterDate(ee.Date.fromYMD(inputData['year_start'], 1,1), ee.Date.fromYMD(inputData['year_end'], 12,31)).filterBounds(area)
    
    et_pet_collection = et_pet_collection.map(resample_image) #resample

    monthly_et_pet_collection = et_pet_collection # Get the monthly sums
    
    image_monthly_with_W = monthly_et_pet_collection.map(calculate_water_stress) # Calculate water stress

    t_collection_monthly = ee.ImageCollection('ECMWF/ERA5/MONTHLY').filterDate(ee.Date.fromYMD(inputData['year_start'], 1,1), ee.Date.fromYMD(inputData['year_end'], 12,31)).filterBounds(area).map(resample_image)

    ndvi_collection = ndvi.get_collection(location['name'])

    image_monthly_with_LUE = image_monthly_with_W.map(calculate_LUE)

    image_monthly_with_LUE = image_monthly_with_LUE.set({'name': location['name']})
    collections.append(image_monthly_with_LUE)
    print(f"Finished processing {location['name']}")

print_sample()