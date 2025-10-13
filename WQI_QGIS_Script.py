import processing
from qgis.core import QgsRasterLayer, QgsProject

# File paths
blue_path = "C:/Users/User/Downloads/LC08_L2SP_169062_20190312_20200829_02_T1_SR_B2.tif"
green_path = "C:/Users/User/Downloads/LC08_L2SP_169062_20190312_20200829_02_T1_SR_B3.tif"
red_path = "C:/Users/User/Downloads/LC08_L2SP_169062_20190312_20200829_02_T1_SR_B4.tif"
swir1_path = "C:/Users/User/Downloads/LC08_L2SP_169062_20190312_20200829_02_T1_SR_B6.tif"
aweish_path = "C:/Users/User/Downloads/LC08_169062_20190312_AWEIsh_masked.tif"

output_wqi = "C:/Users/User/Downloads/LC08_169062_20190312_WQI_masked.tif"

# Load layers
blue = QgsRasterLayer(blue_path, "blue")
green = QgsRasterLayer(green_path, "green")
red = QgsRasterLayer(red_path, "red")
swir1 = QgsRasterLayer(swir1_path, "swir1")
aweish = QgsRasterLayer(aweish_path, "aweish")

layers = [green, blue, red, swir1, aweish]

# Validate layers
for layer in layers:
    if not layer.isValid():
        raise Exception(f"Layer {layer.name()} failed to load!")

# Add layers to project
for layer in layers:
    QgsProject.instance().addMapLayer(layer, False)

# WQI formula with AWEIsh masking negative values
# (GREEN + (BLUE - RED) - SWIR1)/(GREEN + (BLUE - RED) + SWIR1) * (AWEIsh>=0) + ((AWEIsh<0)*-9999)
expression = '(( "green@1" + ("blue@1" - "red@1") - "swir1@1") / ("green@1" + ("blue@1" - "red@1") + "swir1@1")) * ("aweish@1" >= 0) + (("aweish@1" < 0) * -9999)'

# Run Raster Calculator
processing.run("qgis:rastercalculator", {
    'EXPRESSION': expression,
    'LAYERS': layers,
    'EXTENT': green.extent(),
    'CRS': green.crs(),
    'OUTPUT': output_wqi,
    'CELLSIZE': green.rasterUnitsPerPixelX(),
    'NO_DATA': -9999,
    'RASTER_BAND': 1
})

print("WQI calculation finished!")
