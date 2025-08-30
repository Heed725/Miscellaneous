import ee
from ee_plugin import Map

# Initialize Earth Engine
ee.Initialize()

# Load the Amazon canopy tree height dataset
amazonCanopyHeight = ee.Image("projects/sat-io/open-datasets/CTREES/AMAZON-CANOPY-TREE-HT")

# Convert to meters (scale factor 2.5)
actualHeight = amazonCanopyHeight.divide(2.5)

# ColorBrewer Greens palette (light → dark)
visParams = {
    'min': 0,
    'max': 35,
    'palette': [
        '#f7fcf5',  # very light green (low canopy)
        '#e5f5e0',
        '#c7e9c0',
        '#a1d99b',
        '#74c476',
        '#41ab5d',
        '#238b45',
        '#005a32'   # darkest green (tall canopy)
    ]
}

# Add to QGIS map
Map.setCenter(-62, -4, 4)  # Center on the Amazon
Map.addLayer(actualHeight, visParams, 'Amazon Canopy Height (Brewer Greens)')
