import processing
from qgis.core import QgsRasterLayer, QgsProject

# File paths
red_path = "C:/Users/User/Downloads/LC08_L2SP_169062_20190312_20200829_02_T1_SR_B4.tif"
nir_path = "C:/Users/User/Downloads/LC08_L2SP_169062_20190312_20200829_02_T1_SR_B5.tif"
output_ndvi = "C:/Users/User/Downloads/LC08_169062_20190312_NDVI.tif"

# Load layers
red = QgsRasterLayer(red_path, "red")
nir = QgsRasterLayer(nir_path, "nir")

# Make sure layers are valid
if not red.isValid() or not nir.isValid():
    raise Exception("One or more raster layers failed to load!")

# Add layers to the project (required by raster calculator)
QgsProject.instance().addMapLayer(red, False)
QgsProject.instance().addMapLayer(nir, False)

# Run raster calculator
processing.run("qgis:rastercalculator", {
    'EXPRESSION': '("nir@1" - "red@1") / ("nir@1" + "red@1")',
    'LAYERS': [nir, red],
    'EXTENT': nir.extent(),  # use NIR extent
    'CRS': nir.crs(),
    'OUTPUT': output_ndvi,
    'CELLSIZE': nir.rasterUnitsPerPixelX(),
    'NO_DATA': -9999,
    'RASTER_BAND': 1
})

print("NDVI calculation finished!")
