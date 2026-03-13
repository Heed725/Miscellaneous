"""
Split Multipart to Separate Shapefiles
========================================
Run this in the QGIS Python Console.

Your shapefile has 1 feature with 3 geometry parts.
This splits it into 3 separate shapefiles:
  Pugu_part_1.shp, Pugu_part_2.shp, Pugu_part_3.shp
"""

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature,
    QgsVectorFileWriter, QgsCoordinateTransformContext
)
import processing
import os

OUTPUT_DIR = r"C:/Users/user/Documents"

# ---- Find the layer ----
project = QgsProject.instance()
target_layer = None

for layer in project.mapLayers().values():
    if layer.type() == 0:
        if "pug" in layer.name().lower() or "pug" in layer.source().lower():
            target_layer = layer
            break

if target_layer is None:
    target_layer = iface.activeLayer()
    if target_layer is None:
        print("ERROR: No layer found. Select the layer in QGIS and re-run.")
    else:
        print(f"Using active layer: {target_layer.name()}")
else:
    print(f"Found layer: {target_layer.name()}")

if target_layer:
    print(f"  Features: {target_layer.featureCount()}")

    # ---- Multipart to singleparts ----
    print("\nSplitting multipart to singleparts...")
    result = processing.run("native:multiparttosingleparts", {
        'INPUT': target_layer,
        'OUTPUT': 'memory:'
    })

    single_layer = result['OUTPUT']
    part_count = single_layer.featureCount()
    print(f"  Split into {part_count} single parts")

    # ---- Save each part ----
    print(f"\nExporting {part_count} parts...\n")

    geom_type_map = {0: "Point", 1: "LineString", 2: "Polygon"}
    geom_type = geom_type_map.get(single_layer.geometryType(), "Polygon")
    crs = single_layer.crs().authid()

    for i, feature in enumerate(single_layer.getFeatures(), start=1):
        output_path = os.path.join(OUTPUT_DIR, f"Pugu_part_{i}.shp")

        temp_layer = QgsVectorLayer(
            f"{geom_type}?crs={crs}", f"part_{i}", "memory"
        )
        provider = temp_layer.dataProvider()
        provider.addAttributes(single_layer.fields().toList())
        temp_layer.updateFields()

        new_feat = QgsFeature(single_layer.fields())
        new_feat.setGeometry(feature.geometry())
        new_feat.setAttributes(feature.attributes())
        provider.addFeature(new_feat)

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = "UTF-8"

        error = QgsVectorFileWriter.writeAsVectorFormatV3(
            temp_layer, output_path,
            QgsCoordinateTransformContext(), options
        )

        if error[0] == QgsVectorFileWriter.NoError:
            print(f"  Part {i} -> {output_path}")
        else:
            print(f"  ERROR Part {i}: {error}")

    print(f"\nDone! Exported {part_count} shapefiles to {OUTPUT_DIR}")
