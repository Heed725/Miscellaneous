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
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsFields,
    QgsWkbTypes
)

class BBoxToPolygonAlgorithm(QgsProcessingAlgorithm):
    
    BBOX = 'BBOX'
    FORMAT = 'FORMAT'
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
            "Select your coordinate format:\n"
            "• Lat/Lng: minLat,minLng,maxLat,maxLng\n"
            "• Lng/Lat: minLng,minLat,maxLng,maxLat\n\n"
            "Example for Dar es Salaam:\n"
            "Lat/Lng format: -7.00,39.10,-6.65,39.40\n"
            "Lng/Lat format: 39.10,-7.00,39.40,-6.65\n\n"
            "Both formats create the same polygon."
        )
    
    def initAlgorithm(self, config=None):
        
        self.addParameter(
            QgsProcessingParameterString(
                self.BBOX,
                self.tr('Bounding Box Coordinates'),
                defaultValue='-7.00,39.10,-6.65,39.40'
            )
        )
        
        self.addParameter(
            QgsProcessingParameterEnum(
                self.FORMAT,
                self.tr('Coordinate Format'),
                options=[
                    'Lat/Lng (minLat,minLng,maxLat,maxLng)',
                    'Lng/Lat (minLng,minLat,maxLng,maxLat)'
                ],
                defaultValue=0
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
        coord_format = self.parameterAsEnum(parameters, self.FORMAT, context)
        crs = self.parameterAsCrs(parameters, self.CRS, context)
        
        # Parse coordinates
        try:
            coords = [float(x.strip()) for x in bbox_string.split(',')]
            if len(coords) != 4:
                raise ValueError("Must provide exactly 4 coordinates")
        except Exception as e:
            raise ValueError(f"Invalid bounding box format: {str(e)}")
        
        # Interpret coordinates based on selected format
        if coord_format == 0:  # Lat/Lng format
            min_lat, min_lng, max_lat, max_lng = coords
            feedback.pushInfo("Interpreting as: Lat/Lng format")
            feedback.pushInfo(f"  Min Latitude: {min_lat}")
            feedback.pushInfo(f"  Min Longitude: {min_lng}")
            feedback.pushInfo(f"  Max Latitude: {max_lat}")
            feedback.pushInfo(f"  Max Longitude: {max_lng}")
        else:  # Lng/Lat format
            min_lng, min_lat, max_lng, max_lat = coords
            feedback.pushInfo("Interpreting as: Lng/Lat format")
            feedback.pushInfo(f"  Min Longitude: {min_lng}")
            feedback.pushInfo(f"  Min Latitude: {min_lat}")
            feedback.pushInfo(f"  Max Longitude: {max_lng}")
            feedback.pushInfo(f"  Max Latitude: {max_lat}")
        
        # Validate coordinates
        if min_lat >= max_lat:
            raise ValueError(f"Min latitude ({min_lat}) must be less than max latitude ({max_lat})")
        if min_lng >= max_lng:
            raise ValueError(f"Min longitude ({min_lng}) must be less than max longitude ({max_lng})")
        
        # Validate reasonable lat/lng ranges
        if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
            raise ValueError("Latitude values must be between -90 and 90")
        if not (-180 <= min_lng <= 180 and -180 <= max_lng <= 180):
            raise ValueError("Longitude values must be between -180 and 180")
        
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
        # Note: QgsPointXY takes (x, y) which is (longitude, latitude)
        points = [
            QgsPointXY(min_lng, min_lat),  # Bottom-left
            QgsPointXY(max_lng, min_lat),  # Bottom-right
            QgsPointXY(max_lng, max_lat),  # Top-right
            QgsPointXY(min_lng, max_lat),  # Top-left
            QgsPointXY(min_lng, min_lat)   # Close polygon
        ]
        
        # Create feature with polygon geometry
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolygonXY([points]))
        
        # Add feature to sink
        sink.addFeature(feature)
        
        feedback.pushInfo("✓ Polygon created successfully!")
        
        return {self.OUTPUT: dest_id}
