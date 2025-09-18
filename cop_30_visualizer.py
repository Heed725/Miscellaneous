import ee
from ee_plugin import Map

# Initialize Earth Engine
ee.Initialize()

# Load the Copernicus GLO-30 DEM ImageCollection
dem_collection = ee.ImageCollection("COPERNICUS/DEM/GLO30")

# Merge tiles into one image
dem = dem_collection.select('DEM').mosaic()

# Visualization parameters (grayscale)
visParams = {
    'min': 0,
    'max': 6000,  # adjust based on your region
    'palette': ['black', 'white']
}

# Add to QGIS map
Map.setCenter(0, 0, 2)  # Global view
Map.addLayer(dem, visParams, 'Copernicus DEM (Grayscale)')

print("Global Copernicus DEM added to QGIS map in grayscale")
