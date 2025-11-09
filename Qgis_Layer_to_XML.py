"""
QGIS Processing Script: Extract Color Ramps to XML
Extracts color ramps from multiple selected layers and saves them as a combined XML file.
"""

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterFileDestination,
    QgsProcessingException,
    QgsRendererRange,
    QgsRendererCategory,
    QgsColorRampShader,
    QgsRasterRenderer,
    QgsSingleBandPseudoColorRenderer
)
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtXml import QDomDocument
import processing


class ExtractColorRampsAlgorithm(QgsProcessingAlgorithm):
    INPUT_LAYERS = 'INPUT_LAYERS'
    OUTPUT_XML = 'OUTPUT_XML'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExtractColorRampsAlgorithm()

    def name(self):
        return 'extractcolorramps'

    def displayName(self):
        return self.tr('Extract Color Ramps to XML')

    def group(self):
        return self.tr('Color Tools')

    def groupId(self):
        return 'colortools'

    def shortHelpString(self):
        return self.tr("""
        Extracts color ramps from multiple selected layers and combines them into a single XML file.
        
        Supports:
        - Vector layers with graduated or categorized renderers
        - Raster layers with pseudocolor or singleband gray renderers
        
        The output XML file contains all color ramps in QGIS color ramp format.
        """)

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_LAYERS,
                self.tr('Input layers'),
                QgsProcessing.TypeMapLayer
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_XML,
                self.tr('Output XML file'),
                'XML files (*.xml)'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        layers = self.parameterAsLayerList(parameters, self.INPUT_LAYERS, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT_XML, context)

        if not layers:
            raise QgsProcessingException(self.tr('No layers selected'))

        # Create XML document with QGIS style format
        doc = QDomDocument()
        root = doc.createElement('qgis_style')
        root.setAttribute('version', '2')
        doc.appendChild(root)
        
        # Create symbols container (required even if empty)
        symbols = doc.createElement('symbols')
        root.appendChild(symbols)
        
        # Create colorramps container
        colorramps = doc.createElement('colorramps')
        root.appendChild(colorramps)

        total_layers = len(layers)
        color_ramps_found = 0

        for idx, layer in enumerate(layers):
            if feedback.isCanceled():
                break

            feedback.setProgress(int((idx / total_layers) * 100))
            feedback.pushInfo(f'Processing layer: {layer.name()}')

            try:
                ramp_extracted = False

                # Handle vector layers
                if hasattr(layer, 'renderer'):
                    renderer = layer.renderer()
                    
                    # Graduated renderer
                    if renderer.type() == 'graduatedSymbol':
                        color_ramp = renderer.sourceColorRamp()
                        if color_ramp:
                            ramp_elem = self.createColorRampElement(doc, color_ramp, f"{layer.name()}_graduated")
                            colorramps.appendChild(ramp_elem)
                            ramp_extracted = True
                            
                    # Categorized renderer
                    elif renderer.type() == 'categorizedSymbol':
                        color_ramp = renderer.sourceColorRamp()
                        if color_ramp:
                            ramp_elem = self.createColorRampElement(doc, color_ramp, f"{layer.name()}_categorized")
                            colorramps.appendChild(ramp_elem)
                            ramp_extracted = True

                # Handle raster layers
                if hasattr(layer, 'renderer') and hasattr(layer.renderer(), 'shader'):
                    renderer = layer.renderer()
                    
                    # Pseudocolor renderer
                    if isinstance(renderer, QgsSingleBandPseudoColorRenderer):
                        shader = renderer.shader()
                        if shader and shader.rasterShaderFunction():
                            raster_shader = shader.rasterShaderFunction()
                            if isinstance(raster_shader, QgsColorRampShader):
                                color_ramp = raster_shader.sourceColorRamp()
                                if color_ramp:
                                    ramp_elem = self.createColorRampElement(doc, color_ramp, f"{layer.name()}_raster")
                                    colorramps.appendChild(ramp_elem)
                                    ramp_extracted = True

                if ramp_extracted:
                    color_ramps_found += 1
                    feedback.pushInfo(f'  ? Color ramp extracted from {layer.name()}')
                else:
                    feedback.pushInfo(f'  ? No color ramp found in {layer.name()}')

            except Exception as e:
                feedback.reportError(f'Error processing layer {layer.name()}: {str(e)}')

        # Save XML file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(doc.toString(2))
            feedback.pushInfo(f'\n? Successfully saved {color_ramps_found} color ramp(s) to {output_file}')
        except Exception as e:
            raise QgsProcessingException(f'Error writing XML file: {str(e)}')

        return {self.OUTPUT_XML: output_file}

    def createColorRampElement(self, doc, color_ramp, ramp_name):
        """Create XML element for a color ramp"""
        ramp_elem = doc.createElement('colorramp')
        ramp_elem.setAttribute('name', ramp_name)
        ramp_elem.setAttribute('type', color_ramp.type())

        # Get color ramp properties
        props = color_ramp.properties()
        
        # Create Option element with Map type
        option_elem = doc.createElement('Option')
        option_elem.setAttribute('type', 'Map')
        
        # Add each property as an Option child element
        for key, value in props.items():
            prop_option = doc.createElement('Option')
            prop_option.setAttribute('type', 'QString')
            prop_option.setAttribute('name', key)
            prop_option.setAttribute('value', str(value))
            option_elem.appendChild(prop_option)
        
        ramp_elem.appendChild(option_elem)
        
        # Also add prop elements (QGIS uses both formats)
        for key, value in props.items():
            prop_elem = doc.createElement('prop')
            prop_elem.setAttribute('k', key)
            prop_elem.setAttribute('v', str(value))
            ramp_elem.appendChild(prop_elem)

        return ramp_elem


# To use this script in QGIS:
# 1. Open QGIS
# 2. Go to Processing > Toolbox
# 3. Click on the Python icon and select "Add Script to Toolbox..."
# 4. Select this file
# 5. The tool will appear under "Scripts > Color Tools > Extract Color Ramps to XML"
