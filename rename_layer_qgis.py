from qgis.core import QgsProject

# Get the current QGIS project instance
project = QgsProject.instance()

# Get all layers in the project
layers = project.mapLayers().values()

# Filter layers with the name "Dar_Dem.tif"
dar_dem_layers = [layer for layer in layers if layer.name() == "Dar_Dem.tif"]

# Check if we have exactly 20 layers
if len(dar_dem_layers) != 20:
    print(f"Warning: Found {len(dar_dem_layers)} layers named 'Dar_Dem.tif', expected 20")
    print("Proceeding to rename the found layers...")

# Rename each layer starting from Arcmap_28
for i, layer in enumerate(dar_dem_layers, start=28):
    new_name = f"Arcmap_{i}"
    layer.setName(new_name)
    print(f"Renamed layer to: {new_name}")

# Refresh the layer tree
iface.layerTreeView().refreshLayerSymbology(layer.id())

print(f"\nSuccessfully renamed {len(dar_dem_layers)} layers")
