from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterCrs,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsGeometry,
    QgsRectangle,
    QgsFeature,
    QgsFields,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem
)
from qgis.utils import iface
from PyQt5.QtCore import QCoreApplication


class CreateExtentPolygonAlgorithm(QgsProcessingAlgorithm):
    OUTPUT = 'OUTPUT'
    CRS = 'CRS'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CreateExtentPolygonAlgorithm()

    def name(self):
        return 'createextentpolygon'

    def displayName(self):
        return self.tr('Create Polygon from Map Extent')

    def group(self):
        return self.tr('Custom Scripts')

    def groupId(self):
        return 'customscripts'

    def shortHelpString(self):
        return self.tr('Creates a polygon shapefile based on the current map canvas extent')

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('Output CRS'),
                optional=True
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Output Shapefile'),
                fileFilter='Shapefiles (*.shp)'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Get the map canvas
        canvas = iface.mapCanvas()
        
        # Get the current extent
        extent = canvas.extent()
        
        # Get CRS (use specified CRS or canvas CRS)
        crs = self.parameterAsCrs(parameters, self.CRS, context)
        if not crs.isValid():
            crs = canvas.mapSettings().destinationCrs()
        
        # Get output file path
        output_path = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        
        feedback.pushInfo(f'Map Extent: {extent.toString()}')
        feedback.pushInfo(f'CRS: {crs.authid()}')
        
        # Create geometry from extent
        rect_geom = QgsGeometry.fromRect(extent)
        
        # Create fields (empty for basic extent polygon)
        fields = QgsFields()
        
        # Set up the writer
        writer = QgsVectorFileWriter(
            output_path,
            'UTF-8',
            fields,
            QgsWkbTypes.Polygon,
            crs,
            'ESRI Shapefile'
        )
        
        if writer.hasError() != QgsVectorFileWriter.NoError:
            feedback.reportError(f'Error creating shapefile: {writer.errorMessage()}')
            return {}
        
        # Create and add feature
        feature = QgsFeature()
        feature.setGeometry(rect_geom)
        writer.addFeature(feature)
        
        # Clean up
        del writer
        
        feedback.pushInfo(f'Successfully created polygon shapefile: {output_path}')
        
        # Load the created shapefile into QGIS
        layer = QgsVectorLayer(output_path, 'Map Extent Polygon', 'ogr')
        if layer.isValid():
            from qgis.core import QgsProject
            QgsProject.instance().addMapLayer(layer)
            feedback.pushInfo('Layer loaded into QGIS')
        else:
            feedback.reportError('Failed to load layer into QGIS')
        
        return {self.OUTPUT: output_path}


# To use this script in QGIS:
# 1. Open QGIS
# 2. Go to Processing > Toolbox
# 3. Click the Python icon and select "Create New Script from Template"
# 4. Replace the template code with this script
# 5. Save the script
# 6. The tool will appear in the Processing Toolbox under "Custom Scripts"
