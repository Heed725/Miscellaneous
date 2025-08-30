import ee
from ee_plugin import Map

# Initialize Earth Engine
ee.Initialize()

# ------------------------------
# Load ESRI Global LULC 10m Time Series
# ------------------------------
lulc_collection = ee.ImageCollection('projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS')

# 2017 composite
lulc2017 = lulc_collection.filterDate('2017-01-01', '2017-12-31').mosaic()

# ------------------------------
# Remap original classes to 1-9
# ------------------------------
remap_from = [1, 2, 4, 5, 7, 8, 9, 10, 11]
remap_to   = [1, 2, 3, 4, 5, 6, 7, 8, 9]

lulc2017_remapped = lulc2017.remap(remap_from, remap_to)

# ------------------------------
# Visualization parameters
# ------------------------------
visParams = {
    'min': 1,
    'max': 9,
    'palette': [
        "#1A5BAB",  # Water
        "#358221",  # Trees
        "#87D19E",  # Flooded Vegetation
        "#FFDB5C",  # Crops
        "#ED022A",  # Built Area
        "#EDE9E4",  # Bare Ground
        "#F2FAFF",  # Snow/Ice
        "#C8C8C8",  # Clouds
        "#eecfa8"   # Rangeland
    ]
}

# ------------------------------
# Add to QGIS map
# ------------------------------
Map.setCenter(0, 0, 2)  # Center globally
Map.addLayer(lulc2017_remapped, visParams, 'LULC 2017 (Remapped)')

print("2017 LULC layer added to QGIS map with remapped classes and Rangeland color #eecfa8")
