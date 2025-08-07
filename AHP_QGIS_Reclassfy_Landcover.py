from typing import Any, Optional
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterString,
    QgsProcessingParameterRasterDestination,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingException,
    QgsRasterLayer,
)
import processing


class ReclassifyLandcoverPriority(QgsProcessingAlgorithm):
    """
    Reclassify a land cover raster (values 1–5) into new AHP priority values
    (also 1–5), based on user-defined mapping.
    """

    INPUT_RASTER = "INPUT_RASTER"
    RECLASS_RULES = "RECLASS_RULES"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "reclassify_landcover_priority"

    def displayName(self) -> str:
        return "Reclassify Landcover Priority (1–5)"

    def group(self) -> str:
        return "Multi-Criteria Analysis"

    def groupId(self) -> str:
        return "mca"

    def shortHelpString(self) -> str:
        return (
            "Reclassify a landcover raster with values 1 to 5 into AHP priority classes.\n"
            "For example: '1=5;2=4;3=3;4=2;5=1' will reverse the priorities.\n"
            "Output is a new raster with reclassified values (1 = Lowest, 5 = Highest)."
        )

    def initAlgorithm(self, config: Optional[dict[str, Any]] = None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER,
                "Input Landcover Raster (values 1 to 5)"
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.RECLASS_RULES,
                "Reclassification Rules (e.g., '1=5;2=4;3=3;4=2;5=1')",
                defaultValue="1=5;2=4;3=3;4=2;5=1"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                "Output Reclassified Raster (.tif)"
            )
        )

    def processAlgorithm(self, parameters: dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback) -> dict[str, Any]:
        raster_layer = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)
        rules_str = self.parameterAsString(parameters, self.RECLASS_RULES, context)
        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        if not isinstance(raster_layer, QgsRasterLayer):
            raise QgsProcessingException("The input must be a raster layer.")

        try:
            # Convert rules from '1=5;2=4;...' to GDAL format: "1 1 5\n2 2 4\n..."
            rule_lines = []
            for pair in rules_str.split(";"):
                src, dst = pair.strip().split("=")
                rule_lines.append(f"{src} {src} {dst}")
            table_string = "\n".join(rule_lines)
        except Exception:
            raise QgsProcessingException("Invalid format in reclassification rules. Use format like '1=5;2=4;...'")

        feedback.pushInfo("Reclassification Table:\n" + table_string)

        result = processing.run(
            "gdal:reclassifybytable",
            {
                "INPUT_RASTER": raster_layer.source(),
                "RASTER_BAND": 1,
                "TABLE": table_string,
                "NO_DATA": -9999,
                "RANGE_BOUNDARIES": 0,  # min < val <= max
                "DATA_TYPE": 5,         # Float32
                "OUTPUT": output_path,
            },
            context=context,
            feedback=feedback
        )

        return {self.OUTPUT: result['OUTPUT']}

    def createInstance(self):
        return ReclassifyLandcoverPriority()
