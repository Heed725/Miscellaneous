from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsCoordinateReferenceSystem,
    QgsVectorFileWriter,
    QgsProject
)

def create_polygon_from_bbox(bbox_string, output_path, crs_code="EPSG:4326"):
    """
    Create a polygon shapefile from a bounding box string.
    
    Parameters:
    bbox_string (str): Bounding box as "ymin,xmin,ymax,xmax" or "xmin,ymin,xmax,ymax"
    output_path (str): Full path for output shapefile (e.g., '/path/to/output.shp')
    crs_code (str): Coordinate reference system (default: "EPSG:4326" for WGS84)
    """
    
    # Parse the bbox string
    coords = [float(x.strip()) for x in bbox_string.split(',')]
    
    if len(coords) != 4:
        raise ValueError("Bounding box must contain exactly 4 coordinates")
    
    # Assuming format: ymin, xmin, ymax, xmax (lat, lon, lat, lon)
    ymin, xmin, ymax, xmax = coords
    
    # Create memory layer
    crs = QgsCoordinateReferenceSystem(crs_code)
    layer = QgsVectorLayer(f"Polygon?crs={crs_code}", "bbox_polygon", "memory")
    provider = layer.dataProvider()
    
    # Create polygon geometry from bbox coordinates
    points = [
        QgsPointXY(xmin, ymin),  # Bottom-left
        QgsPointXY(xmax, ymin),  # Bottom-right
        QgsPointXY(xmax, ymax),  # Top-right
        QgsPointXY(xmin, ymax),  # Top-left
        QgsPointXY(xmin, ymin)   # Close the polygon
    ]
    
    # Create feature with polygon geometry
    feature = QgsFeature()
    feature.setGeometry(QgsGeometry.fromPolygonXY([points]))
    
    # Add feature to layer
    provider.addFeatures([feature])
    layer.updateExtents()
    
    # Save to shapefile
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"
    options.fileEncoding = "UTF-8"
    
    error = QgsVectorFileWriter.writeAsVectorFormatV3(
        layer,
        output_path,
        QgsProject.instance().transformContext(),
        options
    )
    
    if error[0] == QgsVectorFileWriter.NoError:
        print(f"Shapefile created successfully: {output_path}")
        
        # Load the layer into QGIS
        output_layer = QgsVectorLayer(output_path, "BBox Polygon", "ogr")
        if output_layer.isValid():
            QgsProject.instance().addMapLayer(output_layer)
            print("Layer added to QGIS project")
        else:
            print("Failed to load layer into QGIS")
    else:
        print(f"Error creating shapefile: {error}")
    
    return layer


# Example usage:
# Replace with your actual bbox coordinates and output path
bbox = "38.854980,-7.079088,39.799804,-6.446318"
output_shapefile = "/path/to/your/output/bbox_polygon.shp"

# Create the polygon
create_polygon_from_bbox(bbox, output_shapefile)
