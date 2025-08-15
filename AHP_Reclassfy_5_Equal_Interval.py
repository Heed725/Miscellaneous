from typing import Any, Optional
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterBoolean,
    QgsRasterLayer,
    QgsProcessingException,
)
import processing
import os


class ReclassifySingleRasterSaveTIF(QgsProcessingAlgorithm):
    INPUT_RASTER = "INPUT_RASTER"
    OUTPUT_RASTER = "OUTPUT_RASTER"
    LOAD_OUTPUT = "LOAD_OUTPUT"

    def name(self) -> str:
        return "reclassify_single_raster_save_tif"

    def displayName(self) -> str:
        return "Reclassify Single Raster (Save as .tif)"

    def group(self) -> str:
        return "Multi-Criteria Analysis"

    def groupId(self) -> str:
        return "mca"

    def shortHelpString(self) -> str:
        return (
            "Reclassifies a single raster layer into 5 equal-interval classes. "
            "The output is saved as a user-defined .tif file."
        )

    def initAlgorithm(self, config: Optional[dict[str, Any]] = None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER,
                "Input Raster Layer"
            )
        )
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_RASTER,
                "Output Reclassified Raster (.tif)",
                fileFilter="TIFF files (*.tif)"
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.LOAD_OUTPUT,
                "Load output to QGIS project",
                defaultValue=True
            )
        )

    def processAlgorithm(
        self,
        parameters: dict[str, Any],
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback
    ) -> dict[str, Any]:

        raster: QgsRasterLayer = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)
        output_path = self.parameterAsFile(parameters, self.OUTPUT_RASTER, context)
        load_output = self.parameterAsBoolean(parameters, self.LOAD_OUTPUT, context)

        if not raster:
            raise QgsProcessingException("Invalid raster layer.")

        # Get min and max values
        stats = raster.dataProvider().bandStatistics(1)
        min_val = stats.minimumValue
        max_val = stats.maximumValue

        if min_val == max_val:
            raise QgsProcessingException(f"No variation in raster values: {min_val}")

        interval = (max_val - min_val) / 5
        breakpoints = [min_val + i * interval for i in range(6)]
        feedback.pushInfo(f"Breakpoints: {[round(b, 2) for b in breakpoints]}")

        # Escape double quotes in the raster name if needed
        raster_name = raster.name().replace('"', '""')
        band_ref = f'"{raster_name}@1"'

        # Build expression dynamically using actual raster name
        expr = (
            f"if({band_ref} >= {breakpoints[4]}, 5, "
            f"if({band_ref} >= {breakpoints[3]}, 4, "
            f"if({band_ref} >= {breakpoints[2]}, 3, "
            f"if({band_ref} >= {breakpoints[1]}, 2, 1))))"
        )

        extent = raster.extent()
        extent_str = f"{extent.xMinimum()},{extent.xMaximum()},{extent.yMinimum()},{extent.yMaximum()} [{raster.crs().authid()}]"

        calc_params = {
            'EXPRESSION': expr,
            'LAYERS': [raster],
            'CELLSIZE': 0,
            'EXTENT': extent_str,
            'CRS': raster.crs().authid(),
            'OUTPUT': output_path
        }

        result = processing.run(
            "qgis:rastercalculator",
            calc_params,
            context=context,
            feedback=feedback
        )

        actual_output = result["OUTPUT"]

        if load_output and hasattr(context, 'addLayerToLoadOnCompletion'):
            context.addLayerToLoadOnCompletion(
                actual_output,
                context.LayerDetails(
                    os.path.splitext(os.path.basename(output_path))[0],
                    context.project(),
                    actual_output
                )
            )

        feedback.pushInfo(f"Reclassified raster saved to: {actual_output}")
        return {self.OUTPUT_RASTER: actual_output}

    def createInstance(self):
        return ReclassifySingleRasterSaveTIF()
