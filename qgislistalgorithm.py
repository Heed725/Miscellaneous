import processing
from qgis.core import QgsApplication

# List ALL algorithms
print("=== ALL PROCESSING ALGORITHMS ===\n")
for alg in QgsApplication.processingRegistry().algorithms():
    print(alg.id())
