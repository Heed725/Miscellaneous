from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterBand,
    QgsProcessingParameterFileDestination,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsRasterBlock,
    QgsProcessingException,
    QgsPalettedRasterRenderer,
)
import csv
import os
import tempfile


class RasterUniqueValuesReportToCSVAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    BAND = 'BAND'
    OUTPUT_CSV = 'OUTPUT_CSV'

    def tr(self, text):
        return QCoreApplication.translate('RasterUniqueValuesReportToCSV', text)

    def createInstance(self):
        return RasterUniqueValuesReportToCSVAlgorithm()

    def name(self):
        return 'rasteruniquevaluesreportcsv'

    def displayName(self):
        return self.tr('Raster Unique Values Report (CSV)')

    def group(self):
        return self.tr('Raster analysis')

    def groupId(self):
        return 'rasteranalysis'

    def shortHelpString(self):
        return self.tr('Counts unique values in a raster layer and exports to CSV with labels, colors, and percentages.')

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(self.INPUT, self.tr('Raster layer'))
        )
        self.addParameter(
            QgsProcessingParameterBand(self.BAND, self.tr('Band number'), 1, parentLayerParameterName=self.INPUT)
        )
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_CSV,
                self.tr('Output CSV file'),
                fileFilter='CSV files (*.csv)',
                optional=True
            )
        )

    def processAlgorithm(self, parameters, context: QgsProcessingContext, feedback: QgsProcessingFeedback):
        raster = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        band = self.parameterAsInt(parameters, self.BAND, context)
        output_csv = self.parameterAsFileOutput(parameters, self.OUTPUT_CSV, context)

        if not output_csv:
            output_csv = os.path.join(tempfile.gettempdir(), 'raster_unique_values.csv')
            feedback.pushInfo(f"No output file specified. Using temporary file: {output_csv}")

        provider = raster.dataProvider()
        extent = raster.extent()
        width = raster.width()
        height = raster.height()
        nodata = provider.sourceNoDataValue(band)

        feedback.pushInfo(f"Nodata value: {nodata}")
        unique_values = {}

        block = provider.block(band, extent, width, height)
        if not block:
            raise QgsProcessingException("Could not read raster block.")

        for row in range(height):
            for col in range(width):
                value = block.value(row, col)
                if nodata is not None and (value == nodata or str(value) == 'nan'):
                    continue
                unique_values[value] = unique_values.get(value, 0) + 1

            if row % 10 == 0:
                progress = 100 * row / height
                feedback.setProgress(int(progress))
                if feedback.isCanceled():
                    raise QgsProcessingException("Processing canceled.")

        total_pixels = sum(unique_values.values())
        feedback.pushInfo(f"Total valid pixels: {total_pixels}")

        # Get labels/colors from renderer if available
        renderer = raster.renderer()
        label_map = {}
        if isinstance(renderer, QgsPalettedRasterRenderer):
            for entry in renderer.classes():
                label_map[entry.value] = (entry.label, entry.color.name())

        # Write output to CSV
        with open(output_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Value', 'Count', 'Percentage', 'Label', 'Color'])
            for val, count in sorted(unique_values.items()):
                percent = (count / total_pixels * 100) if total_pixels > 0 else 0
                label, color = label_map.get(val, ("", ""))
                writer.writerow([val, count, f"{percent:.8f}", label, color])

        feedback.pushInfo(f"CSV written to {output_csv}")
        return {self.OUTPUT_CSV: output_csv}
