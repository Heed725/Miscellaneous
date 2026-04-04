from osgeo import gdal
from qgis.core import QgsProject, QgsRasterLayer

layer = QgsProject.instance().mapLayersByName("Magozi_2024")[0]
src = layer.source()

dst = "C:/Users/user/Documents/Magozi_2025_int.tif"

gdal.Translate(
    dst,
    src,
    outputType=gdal.GDT_Byte,
    creationOptions=["COMPRESS=LZW"]
)

new_layer = QgsRasterLayer(dst, "Magozi_2025_int")
QgsProject.instance().addMapLayer(new_layer)

print("Done! Layer added to QGIS:", dst)
