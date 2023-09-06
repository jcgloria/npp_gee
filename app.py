from greppo import app
import ee 

service_account = 'ucl-676@ee-96juancg.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'ee-96juancg-5fded826f6f1.json')
ee.Initialize(credentials)

# Select the satellite dataset from the catalog
dem = ee.Image('USGS/SRTMGL1_003')

# Process it
ee_dem = dem.updateMask(dem.gt(0))

# Provide visualisation parameters
vis_params = {
    'min': 0,
    'max': 4000,
    'palette': ['006633', 'E5FFCC', '662A00', 'D8D8D8', 'F5F5F5']}

app.ee_layer(ee_object=ee_dem, vis_params=vis_params, name='DEM', 
             description='World Digital Elevation Map from GEE')

multiselect1 = app.multiselect(
    name="Second selector", options=["Asia", "Africa", "Europe"], default=["Asia"]
)

text_1 = app.text(value='Enter text', name="text input 1")



select1 = app.select(name="First selector", options=["a", "b", "c"], default="a")

