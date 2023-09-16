# Google Earth Engine scripts to calculate net primary productivity. 

This application uses satellite imagery available in Google Earth Engine to calculate the net primary productivity (NPP), or the amount of carbon stored by an ecosystem per unit of area. The NPP is a product of 3 parameters, the NDVI, LUE, and PAR.

- https://developers.google.com/earth-engine/apidocs

- `ndvi.py` calculates the Normalized Difference Vegetation Index
- `lue.py` calculates the Light Use Efficiency
- `par.py` calculates the Photosynthetically Active Radiation
- `main.py` calculates the Net Primary Productivity using the product of the above three scripts
  
<img width="516" alt="ucl_app" src="https://github.com/jcgloria/npp_gee/assets/30906750/5d3ee9e7-9b17-4307-bf6a-2cad75d3217b">

This application is part of a dissertation project required by the MSc Emerging Digital Technologies programme in UCL. 
