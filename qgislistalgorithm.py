import processing
from qgis.core import QgsApplication

# List ALL algorithms
print("=== ALL PROCESSING ALGORITHMS ===\n")
for alg in QgsApplication.processingRegistry().algorithms():
    print(alg.id())

output_path = "C:/Users/ ... /Desktop/qgis_algorithms.txt"

with open(output_path, 'w') as f:
    for alg in QgsApplication.processingRegistry().algorithms():
        f.write(f"{alg.id()} | {alg.displayName()}\n")

print(f"Saved to {output_path}")
