# Visualize Global Facebook Meta Canopy Height in QGIS
# Custom dark green palette (HCL-inspired)
# Dataset: projects/sat-io/open-datasets/facebook/meta-canopy-height
# Author: Hemed Lungo

import ee
from ee_plugin import Map

# Initialize Earth Engine
ee.Initialize()

# Load Meta Global Canopy Height dataset
canopy_ht = ee.ImageCollection("projects/sat-io/open-datasets/facebook/meta-canopy-height") \
    .mosaic()

# Custom dark HCL-style green palette (low → high)
greens_dark_hcl = [
    '#B4DCAB',  # light green
    '#81C07A',  # medium-light green
    '#419F44',  # medium green
    '#1F7330',  # dark green
    '#004616'   # very dark green
]

# Visualization parameters
vis_params = {
    'min': 0,
    'max': 50,
    'palette': greens_dark_hcl
}

# Center map globally and visualize
Map.setCenter(0, 0, 2)
Map.addLayer(canopy_ht, vis_params, 'Meta Canopy Height (Dark Greens)')
