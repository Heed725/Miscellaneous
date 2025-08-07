from typing import Any, Optional
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingException,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterString,
    QgsProcessingParameterRasterDestination,
    QgsRasterLayer,
)
import processing


class AHPRasterOverlayMultipleAlgorithm(QgsProcessingAlgorithm):
    """
    AHP Raster Overlay for any number of input rasters with given weights.
    """

    INPUT_RASTERS = "INPUT_RASTERS"
    WEIGHTS = "WEIGHTS"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "ahp_raster_overlay_multiple"

    def displayName(self) -> str:
        return "AHP Raster Overlay"

    def group(self) -> str:
        return "Multi-Criteria Analysis"

    def groupId(self) -> str:
        return "mca"

    def shortHelpString(self) -> str:
        return (
            "Combines multiple reclassified raster layers using AHP weights "
            "to produce a weighted overlay raster."
        )

    def initAlgorithm(self, config: Optional[dict[str, Any]] = None):
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_RASTERS,
                "Input Raster Layers (minimum 2)",
                layerType=QgsProcessing.TypeRaster
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.WEIGHTS,
                "Weights (comma-separated, e.g. 0.3,0.5,0.2)",
                defaultValue="0.5,0.3,0.2"
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                "Weighted Overlay Output (.tif)"
            )
        )

    def processAlgorithm(
        self,
        parameters: dict[str, Any],
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback
    ) -> dict[str, Any]:

        raster_layers = self.parameterAsLayerList(parameters, self.INPUT_RASTERS, context)
        weights_str = self.parameterAsString(parameters, self.WEIGHTS, context)

        if len(raster_layers) < 2:
            raise QgsProcessingException("Please provide at least two raster layers.")

        try:
            weights = [float(w.strip()) for w in weights_str.split(",")]
        except Exception:
            raise QgsProcessingException("Weights must be a comma-separated list of numbers.")

        if len(weights) != len(raster_layers):
            raise QgsProcessingException("Number of weights must match number of raster layers.")

        total_weight = sum(weights)
        if total_weight == 0:
            raise QgsProcessingException("Sum of weights must be greater than zero.")

        weights = [w / total_weight for w in weights]
        feedback.pushInfo(f"Normalized weights: {weights}")

        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        variables = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if len(raster_layers) > len(variables):
            raise QgsProcessingException(f"Too many input rasters! Max supported: {len(variables)}")

        expression_terms = []
        params = {
            'NO_DATA': -9999,
            'RTYPE': 5,  # Float32 output
            'OPTIONS': '',
            'EXTRA': '',
            'OUTPUT': output_path,
        }

        for i, (layer, weight) in enumerate(zip(raster_layers, weights)):
            var = variables[i]
            key_in = f"INPUT_{var}"
            key_band = f"BAND_{var}"

            if isinstance(layer, QgsRasterLayer):
                raster_path = layer.source()
            else:
                raise QgsProcessingException(f"Invalid raster layer at index {i}.")

            params[key_in] = raster_path
            params[key_band] = 1
            expression_terms.append(f"{weight}*{var}")

        expression = " + ".join(expression_terms)
        params['FORMULA'] = expression

        feedback.pushInfo(f"Raster calculator expression: {expression}")

        result = processing.run(
            "gdal:rastercalculator",
            params,
            context=context,
            feedback=feedback
        )

        feedback.pushInfo(f"Weighted overlay raster saved to: {result['OUTPUT']}")

        return {self.OUTPUT: result['OUTPUT']}

    def createInstance(self):
        return AHPRasterOverlayMultipleAlgorithm()
