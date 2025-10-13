import processing
from qgis.core import QgsRasterLayer, QgsProject

# File paths
blue_path = "C:/Users/User/Downloads/LC08_L2SP_169062_20190312_20200829_02_T1_SR_B2.tif"
green_path = "C:/Users/User/Downloads/LC08_L2SP_169062_20190312_20200829_02_T1_SR_B3.tif"
nir_path = "C:/Users/User/Downloads/LC08_L2SP_169062_20190312_20200829_02_T1_SR_B5.tif"
swir1_path = "C:/Users/User/Downloads/LC08_L2SP_169062_20190312_20200829_02_T1_SR_B6.tif"
swir2_path = "C:/Users/User/Downloads/LC08_L2SP_169062_20190312_20200829_02_T1_SR_B7.tif"

output_aweish = "C:/Users/User/Downloads/LC08_169062_20190312_AWEIsh_masked.tif"

# Load layers
blue = QgsRasterLayer(blue_path, "blue")
green = QgsRasterLayer(green_path, "green")
nir = QgsRasterLayer(nir_path, "nir")
swir1 = QgsRasterLayer(swir1_path, "swir1")
swir2 = QgsRasterLayer(swir2_path, "swir2")

layers = [blue, green, nir, swir1, swir2]

# Check validity
for layer in layers:
    if not layer.isValid():
        raise Exception(f"Layer {layer.name()} failed to load!")

# Add layers to project (required for raster calculator)
for layer in layers:
    QgsProject.instance().addMapLayer(layer, False)

# Raster Calculator formula for AWEIsh with masking negative values
# formula: max(A + 2.5*B - 1.5*(C+D) - 0.25*E, -9999)
expression = '(( "blue@1" + 2.5*"green@1" - 1.5*("nir@1"+"swir1@1") - 0.25*"swir2@1") * (("blue@1" + 2.5*"green@1" - 1.5*("nir@1"+"swir1@1") - 0.25*"swir2@1")>=0) + (("blue@1" + 2.5*"green@1" - 1.5*("nir@1"+"swir1@1") - 0.25*"swir2@1")<0)*-9999 )'

# Run Raster Calculator
processing.run("qgis:rastercalculator", {
    'EXPRESSION': expression,
    'LAYERS': layers,
    'EXTENT': nir.extent(),  # use NIR extent
    'CRS': nir.crs(),
    'OUTPUT': output_aweish,
    'CELLSIZE': nir.rasterUnitsPerPixelX(),
    'NO_DATA': -9999,
    'RASTER_BAND': 1
})

print("AWEIsh calculation with negative masking finished!")
