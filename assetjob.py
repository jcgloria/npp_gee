import ee

# Script to do mass asset operations

service_account = 'ucl-676@ee-96juancg.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'ee-96juancg-5fded826f6f1.json')
ee.Initialize(credentials)

list = ee.data.listAssets('projects/ee-96juancg/assets')

for asset in list['assets']:
    print(asset['id'])
    ee.data.deleteAsset(asset['id'])