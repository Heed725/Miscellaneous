"""
QGIS Processing Script: Generate and Save Legend Patch Shapes
This script creates legend patch shapes from polygons and saves them directly to QGIS or exports as XML
"""

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterEnum,
    QgsProcessingParameterString,
    QgsWkbTypes,
    QgsStyle,
    QgsGeometry,
    QgsLegendPatchShape,
    QgsSymbol
)
from qgis.PyQt.QtCore import QCoreApplication
import xml.etree.ElementTree as ET
from xml.dom import minidom


class GenerateLegendPatchShapesAlgorithm(QgsProcessingAlgorithm):
    
    INPUT_LAYER = 'INPUT_LAYER'
    NAME_FIELD = 'NAME_FIELD'
    TAG_FIELD = 'TAG_FIELD'
    OUTPUT_MODE = 'OUTPUT_MODE'
    OUTPUT_FILE = 'OUTPUT_FILE'
    
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
    
    def createInstance(self):
        return GenerateLegendPatchShapesAlgorithm()
    
    def name(self):
        return 'generatelegendpatchshapes'
    
    def displayName(self):
        return self.tr('Generate and Save Legend Patch Shapes')
    
    def group(self):
        return self.tr('Custom Tools')
    
    def groupId(self):
        return 'customtools'
    
    def shortHelpString(self):
        return self.tr("""
        This algorithm generates legend patch shapes from polygon features.
        
        Parameters:
        - Input Layer: Polygon layer containing the shapes
        - Name Field: Field containing the name for each legend patch shape
        - Tag Field: (Optional) Field containing tags for categorization
        - Output Mode: Choose to save to QGIS, export as XML, or both
        - Output File: Path for XML file (required if exporting XML)
        
        Saved shapes can be accessed via Settings > Style Manager > Legend Patch Shapes
        """)
    
    def initAlgorithm(self, config=None):
        # Input polygon layer
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_LAYER,
                self.tr('Input polygon layer'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        
        # Name field
        self.addParameter(
            QgsProcessingParameterField(
                self.NAME_FIELD,
                self.tr('Name field'),
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.String
            )
        )
        
        # Tag field (optional)
        self.addParameter(
            QgsProcessingParameterField(
                self.TAG_FIELD,
                self.tr('Tag field (optional)'),
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.String,
                optional=True
            )
        )
        
        # Output mode dropdown
        self.addParameter(
            QgsProcessingParameterEnum(
                self.OUTPUT_MODE,
                self.tr('Output mode'),
                options=[
                    'Save to QGIS Style Manager',
                    'Export as XML file',
                    'Both (Save to QGIS and Export XML)'
                ],
                defaultValue=0
            )
        )
        
        # Output XML file (conditional)
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_FILE,
                self.tr('Output XML file'),
                fileFilter='XML files (*.xml)',
                optional=True
            )
        )
    
    def create_xml_structure(self, features_data):
        """Create XML structure for legend patch shapes"""
        root = ET.Element('qgis_style', version="2")
        
        # Add empty standard elements
        ET.SubElement(root, 'symbols')
        ET.SubElement(root, 'colorramps')
        ET.SubElement(root, 'textformats')
        ET.SubElement(root, 'labelsettings')
        
        # Create legendpatchshapes element
        legendpatchshapes = ET.SubElement(root, 'legendpatchshapes')
        
        for name, tags, wkt in features_data:
            # Create legendpatchshape element
            patch = ET.SubElement(legendpatchshapes, 'legendpatchshape')
            patch.set('name', str(name))
            patch.set('tags', str(tags))
            
            # Create definition element with WKT
            definition = ET.SubElement(patch, 'definition')
            definition.set('wkt', wkt)
            definition.set('type', '2')  # 2 = Polygon
            definition.set('preserveAspect', '1')
        
        return root
    
    def export_xml(self, root, output_file):
        """Export XML to file with pretty formatting"""
        xml_string = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        # Remove extra blank lines
        pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
    
    def save_to_qgis_style(self, features_data, feedback):
        """Save legend patch shapes directly to QGIS default style"""
        style = QgsStyle.defaultStyle()
        saved_count = 0
        skipped_count = 0
        
        for name, tags, wkt in features_data:
            # Create QgsGeometry from WKT
            geom = QgsGeometry.fromWkt(wkt)
            
            if geom.isNull() or geom.isEmpty():
                feedback.reportError(f'Invalid geometry for "{name}", skipping')
                skipped_count += 1
                continue
            
            # Create legend patch shape
            patch_shape = QgsLegendPatchShape(
                QgsSymbol.Fill,  # Symbol type for polygon
                geom,
                True  # Preserve aspect ratio
            )
            
            # Parse tags
            tag_list = []
            if tags:
                tag_list = [tag.strip() for tag in str(tags).split(',') if tag.strip()]
            
            # Check if name already exists
            if style.legendPatchShapeNames().count(name) > 0:
                feedback.pushInfo(f'Legend patch shape "{name}" already exists, overwriting...')
                style.removeLegendPatchShape(name)
            
            # Add to style
            success = style.addLegendPatchShape(name, patch_shape, True)
            
            if success:
                # Add tags
                if tag_list:
                    for tag in tag_list:
                        style.tagSymbol(QgsStyle.LegendPatchShapeEntity, name, [tag])
                saved_count += 1
                feedback.pushInfo(f'Saved: "{name}"' + (f' (tags: {", ".join(tag_list)})' if tag_list else ''))
            else:
                feedback.reportError(f'Failed to save "{name}"')
                skipped_count += 1
        
        return saved_count, skipped_count
    
    def processAlgorithm(self, parameters, context, feedback):
        # Get parameters
        layer = self.parameterAsVectorLayer(parameters, self.INPUT_LAYER, context)
        name_field = self.parameterAsString(parameters, self.NAME_FIELD, context)
        tag_field = self.parameterAsString(parameters, self.TAG_FIELD, context)
        output_mode = self.parameterAsEnum(parameters, self.OUTPUT_MODE, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT_FILE, context)
        
        # Determine what to do based on output mode
        # 0 = Save to QGIS only
        # 1 = Export XML only
        # 2 = Both
        save_to_qgis = output_mode in [0, 2]
        export_xml = output_mode in [1, 2]
        
        # Check layer validity
        if layer is None:
            raise Exception(self.tr('Invalid input layer'))
        
        if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            raise Exception(self.tr('Input layer must contain polygon geometries'))
        
        # If export XML is selected but no file specified
        if export_xml and not output_file:
            raise Exception(self.tr('Please specify an output file path for XML export'))
        
        # Collect feature data
        features_data = []
        total = layer.featureCount()
        features = layer.getFeatures()
        
        feedback.pushInfo('Processing features...')
        
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break
            
            # Get feature name
            name = feature[name_field]
            if not name:
                feedback.reportError(f'Feature {feature.id()} has no name, skipping')
                continue
            
            # Get tags
            tags = feature[tag_field] if tag_field else ''
            
            # Get geometry
            geom = feature.geometry()
            if geom.isNull() or geom.isEmpty():
                feedback.reportError(f'Feature {feature.id()} has invalid geometry, skipping')
                continue
            
            # Convert to WKT
            wkt = geom.asWkt()
            
            features_data.append((name, tags, wkt))
            
            # Update progress
            feedback.setProgress(int((current / total) * 100))
        
        if not features_data:
            raise Exception(self.tr('No valid features found to process'))
        
        results = {}
        
        # Save to QGIS
        if save_to_qgis:
            feedback.pushInfo('\n=== Saving to QGIS Style Manager ===')
            saved_count, skipped_count = self.save_to_qgis_style(features_data, feedback)
            feedback.pushInfo(f'\nSuccessfully saved {saved_count} legend patch shapes to QGIS')
            if skipped_count > 0:
                feedback.pushInfo(f'Skipped {skipped_count} shapes due to errors')
            feedback.pushInfo('Access them via: Settings > Style Manager > Legend Patch Shapes')
        
        # Export XML
        if export_xml and output_file:
            feedback.pushInfo('\n=== Exporting XML ===')
            root = self.create_xml_structure(features_data)
            self.export_xml(root, output_file)
            feedback.pushInfo(f'Successfully exported {len(features_data)} legend patch shapes to XML')
            feedback.pushInfo(f'File location: {output_file}')
            results[self.OUTPUT_FILE] = output_file
        
        feedback.pushInfo(f'\n=== Summary ===')
        feedback.pushInfo(f'Total shapes processed: {len(features_data)}')
        
        return results


# Installation Instructions:
# 1. Save this file as generate_legend_patches.py
# 2. Open QGIS Processing Toolbox
# 3. Click Scripts dropdown > Add Script to Toolbox
# 4. Browse to this file
# 5. Tool appears under Scripts > Custom Tools
#
# Usage:
# - Check "Save to QGIS" to add shapes directly to Style Manager
# - Check "Export as XML" to also save as XML file for sharing
# - Access saved shapes: Settings > Style Manager > Legend Patch Shapes
