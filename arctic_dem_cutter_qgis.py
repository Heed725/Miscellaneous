exec("""
import os
import numpy as np
from osgeo import gdal, ogr
from qgis.core import *
import processing
import tempfile

gdal.UseExceptions()

project = QgsProject.instance()

# Find existing layers
mask = project.mapLayersByName("aaa")[0]

dem = next(
    layer for layer in project.mapLayers().values()
    if isinstance(layer, QgsRasterLayer)
    and "ETOPO" in layer.name()
)

folder = r"C:/Users/Admin/Downloads"
temp = tempfile.mkdtemp(prefix="arctic_dem_")

output = os.path.join(
    folder, "North_Pole_Italy_Clipped_DEM.tif"
)

print("STEP 1: Repairing mask geometry...")

fixed = processing.run(
    "native:fixgeometries",
    {
        "INPUT": mask,
        "METHOD": 1,
        "OUTPUT": "memory:"
    }
)["OUTPUT"]

print("STEP 2: Reprojecting mask to WGS84...")

wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")

fixed = processing.run(
    "native:reprojectlayer",
    {
        "INPUT": fixed,
        "TARGET_CRS": wgs84,
        "OUTPUT": "memory:"
    }
)["OUTPUT"]

fixed = processing.run(
    "native:fixgeometries",
    {
        "INPUT": fixed,
        "METHOD": 1,
        "OUTPUT": "memory:"
    }
)["OUTPUT"]

mask_file = os.path.join(temp, "mask.gpkg")

processing.run(
    "native:savefeatures",
    {
        "INPUT": fixed,
        "OUTPUT": mask_file
    }
)

print("STEP 3: Extracting northern DEM...")

subset_file = os.path.join(temp, "subset.tif")

subset = gdal.Translate(
    subset_file,
    dem.source(),
    projWin=[-180, 90, 180, 38.5],
    outputType=gdal.GDT_Float32,
    creationOptions=[
        "COMPRESS=LZW",
        "TILED=YES"
    ]
)

cols = subset.RasterXSize
rows = subset.RasterYSize

print("Raster size:", cols, "x", rows)

print("STEP 4: Rasterizing the land mask...")

vector = ogr.Open(mask_file)
vector_layer = vector.GetLayer()

mask_raster = gdal.GetDriverByName("MEM").Create(
    "", cols, rows, 1, gdal.GDT_Byte
)

mask_raster.SetGeoTransform(
    subset.GetGeoTransform()
)

mask_raster.SetProjection(
    subset.GetProjection()
)

mask_raster.GetRasterBand(1).Fill(0)

gdal.RasterizeLayer(
    mask_raster,
    [1],
    vector_layer,
    burn_values=[1]
)

print("STEP 5: Clipping DEM to land...")

clipped_file = os.path.join(temp, "land_dem.tif")

clipped = gdal.GetDriverByName("GTiff").Create(
    clipped_file,
    cols,
    rows,
    1,
    gdal.GDT_Float32,
    options=["COMPRESS=LZW", "TILED=YES"]
)

clipped.SetGeoTransform(subset.GetGeoTransform())
clipped.SetProjection(subset.GetProjection())

band = clipped.GetRasterBand(1)
band.SetNoDataValue(-9999)

source_nodata = subset.GetRasterBand(1).GetNoDataValue()
land_pixels = 0

for y in range(0, rows, 256):

    height = min(256, rows - y)

    elevation = subset.ReadAsArray(
        0, y, cols, height
    ).astype(np.float32)

    land = mask_raster.ReadAsArray(
        0, y, cols, height
    )

    land_pixels += np.count_nonzero(land)

    if source_nodata is not None:
        elevation[elevation == source_nodata] = -9999

    elevation[~np.isfinite(elevation)] = -9999
    elevation[land == 0] = -9999

    band.WriteArray(elevation, 0, y)

band.FlushCache()
band = None
clipped = None
subset = None
vector = None
mask_raster = None

if land_pixels == 0:
    raise RuntimeError("The mask contains no matching land pixels.")

print("STEP 6: Creating circular North Pole DEM...")

polar_crs = QgsCoordinateReferenceSystem(
    "ESRI:102016"
)

result = gdal.Warp(
    output,
    clipped_file,
    dstSRS=polar_crs.toWkt(),
    xRes=2000,
    yRes=2000,
    resampleAlg="bilinear",
    srcNodata=-9999,
    dstNodata=-9999,
    multithread=True,
    creationOptions=[
        "COMPRESS=LZW",
        "TILED=YES",
        "BIGTIFF=IF_SAFER"
    ]
)

result.FlushCache()
result = None

print("STEP 7: Loading final DEM...")

final_layer = QgsRasterLayer(
    output,
    "North Pole - Italy Clipped DEM"
)

if not final_layer.isValid():
    raise RuntimeError("Output raster could not be loaded.")

project.addMapLayer(final_layer)
project.setCrs(polar_crs)

# Hide other layers
for node in project.layerTreeRoot().findLayers():
    node.setItemVisibilityChecked(
        node.layerId() == final_layer.id()
    )

iface.mapCanvas().setExtent(final_layer.extent())
iface.mapCanvas().refresh()

print("-----------------------------------")
print("SUCCESSFULLY COMPLETED")
print("Saved to:", output)
print("-----------------------------------")
""")
