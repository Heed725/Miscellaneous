from qgis.core import (
    QgsProject,
    QgsVectorLayer
)
import processing

# Load the layer (already loaded in QGIS)
layer = QgsProject.instance().mapLayersByName("Tanzania_Basin")[0]

# Run the dissolve algorithm on the 'name' field
dissolved = processing.run(
    "native:dissolve",
    {
        'INPUT': layer,
        'FIELD': ['name'],  # Dissolve by 'name'
        'OUTPUT': 'memory:'  # Keep result in memory
    }
)['OUTPUT']

# Add dissolved layer to the project
QgsProject.instance().addMapLayer(dissolved)

print("Dissolve completed — duplicates merged by 'name'")
