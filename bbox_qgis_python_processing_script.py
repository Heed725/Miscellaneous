"""
BBox to Polygon Shapefile
Creates a polygon shapefile from bounding box coordinates
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterString,
    QgsProcessingParameterCrs,
    QgsProcessingParameterFeatureSink,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsFields,
    QgsWkbTypes
)

class BBoxToPolygonAlgorithm(QgsProcessingAlgorithm):
    
    BBOX = 'BBOX'
    CRS = 'CRS'
    OUTPUT = 'OUTPUT'
    
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
    
    def createInstance(self):
        return BBoxToPolygonAlgorithm()
    
    def name(self):
        return 'bboxtopolygon'
    
    def displayName(self):
        return self.tr('Create Polygon from BBox')
    
    def group(self):
        return self.tr('Vector creation')
    
    def groupId(self):
        return 'vectorcreation'
    
    def shortHelpString(self):
        return self.tr(
            "Creates a polygon from bounding box coordinates.\n\n"
            "Input format: ymin,xmin,ymax,xmax\n"
            "Example: 38.854980,-7.079088,39.799804,-6.446318\n\n"
            "This represents:\n"
            "- ymin (bottom latitude): 38.854980\n"
            "- xmin (left longitude): -7.079088\n"
            "- ymax (top latitude): 39.799804\n"
            "- xmax (right longitude): -6.446318"
        )
    
    def initAlgorithm(self, config=None):
        
        self.addParameter(
            QgsProcessingParameterString(
                self.BBOX,
                self.tr('Bounding Box Coordinates (ymin,xmin,ymax,xmax)'),
                defaultValue='38.854980,-7.079088,39.799804,-6.446318'
            )
        )
        
        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('Coordinate Reference System'),
                defaultValue='EPSG:4326'
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output Polygon')
            )
        )
    
    def processAlgorithm(self, parameters, context, feedback):
        
        # Get parameters
        bbox_string = self.parameterAsString(parameters, self.BBOX, context)
        crs = self.parameterAsCrs(parameters, self.CRS, context)
        
        # Parse bounding box coordinates
        try:
            coords = [float(x.strip()) for x in bbox_string.split(',')]
            if len(coords) != 4:
                raise ValueError("Must provide exactly 4 coordinates")
            ymin, xmin, ymax, xmax = coords
        except Exception as e:
            raise ValueError(f"Invalid bounding box format: {str(e)}")
        
        # Validate coordinates
        if ymin >= ymax:
            raise ValueError("ymin must be less than ymax")
        if xmin >= xmax:
            raise ValueError("xmin must be less than xmax")
        
        feedback.pushInfo(f"Creating polygon with bounds:")
        feedback.pushInfo(f"  X: {xmin} to {xmax}")
        feedback.pushInfo(f"  Y: {ymin} to {ymax}")
        
        # Create output sink
        fields = QgsFields()
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.Polygon,
            crs
        )
        
        if sink is None:
            raise ValueError("Could not create output layer")
        
        # Create polygon from bounding box
        points = [
            QgsPointXY(xmin, ymin),  # Bottom-left
            QgsPointXY(xmax, ymin),  # Bottom-right
            QgsPointXY(xmax, ymax),  # Top-right
            QgsPointXY(xmin, ymax),  # Top-left
            QgsPointXY(xmin, ymin)   # Close polygon
        ]
        
        # Create feature with polygon geometry
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolygonXY([points]))
        
        # Add feature to sink
        sink.addFeature(feature)
        
        feedback.pushInfo("Polygon created successfully!")
        
        return {self.OUTPUT: dest_id}
