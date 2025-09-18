import ee
from ee_plugin import Map

# Initialize Earth Engine
ee.Initialize()

# ------------------------------
# Load SRTM DEM
# ------------------------------
srtm = ee.Image("USGS/SRTMGL1_003")

# ------------------------------
# Visualization parameters (grayscale)
# ------------------------------
visParams = {
    'min': 0,
    'max': 4000,   # adjust depending on your AOI
    'palette': ['black', 'white']
}

# ------------------------------
# Add to QGIS map
# ------------------------------
Map.setCenter(0, 0, 2)  # Example: Tanzania
Map.addLayer(srtm, visParams, 'SRTM DEM (Grayscale)')

print("SRTM DEM (grayscale) added to QGIS map")
