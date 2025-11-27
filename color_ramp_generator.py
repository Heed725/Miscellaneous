from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterString,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFile,
    QgsStyle,
    QgsColorRamp,
    QgsGradientColorRamp,
    QgsGradientStop
)
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QColor
import re
import csv


class ColorPaletteGeneratorAlgorithm(QgsProcessingAlgorithm):
    COLOR_INPUT = 'COLOR_INPUT'
    PALETTE_NAME = 'PALETTE_NAME'
    PALETTE_TAGS = 'PALETTE_TAGS'
    OUTPUT_FORMAT = 'OUTPUT_FORMAT'
    OUTPUT_MODE = 'OUTPUT_MODE'
    OUTPUT_FILE = 'OUTPUT_FILE'
    CSV_INPUT = 'CSV_INPUT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ColorPaletteGeneratorAlgorithm()

    def name(self):
        return 'generatecolorpalette'

    def displayName(self):
        return self.tr('Generate Color Palette (XML/GPL)')

    def group(self):
        return self.tr('Custom Scripts')

    def groupId(self):
        return 'customscripts'

    def shortHelpString(self):
        return self.tr('''Creates QGIS XML or GIMP GPL color palettes.
        
Enter hex colors comma-separated (e.g., #FF0000,#00FF00,#0000FF80).
Supports #RGB, #RRGGBB, and #RRGGBBAA formats.

Alternatively, import from CSV file with format:
Palette,Tags,Color1,Color2,Color3,...

Choose to import directly into QGIS or export to file.
XML output can be imported to QGIS via Settings > Style Manager > Import.
GPL output can be used in GIMP and other applications.''')

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.CSV_INPUT,
                self.tr('Import from CSV (optional)'),
                behavior=QgsProcessingParameterFile.File,
                fileFilter='CSV files (*.csv)',
                optional=True
            )
        )
        
        self.addParameter(
            QgsProcessingParameterString(
                self.COLOR_INPUT,
                self.tr('Hex Colors (comma-separated)'),
                defaultValue='#1f77b4,#ff7f0e,#2ca02c,#d62728',
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PALETTE_NAME,
                self.tr('Palette Name'),
                defaultValue='MyColorPalette'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PALETTE_TAGS,
                self.tr('Tags (comma-separated)'),
                defaultValue='custom,palette',
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.OUTPUT_MODE,
                self.tr('Output Mode'),
                options=['Import to QGIS', 'Export to File'],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.OUTPUT_FORMAT,
                self.tr('Export Format (if exporting)'),
                options=['QGIS XML', 'GIMP GPL', 'Both'],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_FILE,
                self.tr('Output File (if exporting)'),
                fileFilter='XML files (*.xml);;GPL files (*.gpl);;All files (*.*)',
                optional=True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Get parameters
        csv_file = self.parameterAsFile(parameters, self.CSV_INPUT, context)
        color_input = self.parameterAsString(parameters, self.COLOR_INPUT, context)
        palette_name = self.parameterAsString(parameters, self.PALETTE_NAME, context)
        palette_tags = self.parameterAsString(parameters, self.PALETTE_TAGS, context)
        output_mode = self.parameterAsEnum(parameters, self.OUTPUT_MODE, context)
        output_format = self.parameterAsEnum(parameters, self.OUTPUT_FORMAT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT_FILE, context)

        palettes = []

        # Process CSV if provided
        if csv_file:
            feedback.pushInfo('Reading CSV file...')
            try:
                palettes = self.read_csv_palettes(csv_file, feedback)
                feedback.pushInfo(f'Loaded {len(palettes)} palette(s) from CSV')
            except Exception as e:
                feedback.reportError(f'Error reading CSV: {str(e)}')
                return {}
        
        # Process manual input if no CSV or as additional palette
        if not csv_file or color_input:
            colors = self.parse_hex_colors(color_input, feedback)
            if colors:
                palettes.append({
                    'name': palette_name,
                    'tags': palette_tags,
                    'colors': colors
                })

        if not palettes:
            feedback.reportError('No valid palettes to generate')
            return {}

        # Process based on output mode
        try:
            if output_mode == 0:  # Import to QGIS
                self.import_to_qgis(palettes, feedback)
            else:  # Export to File
                if not output_file:
                    feedback.reportError('Output file must be specified when exporting')
                    return {}
                    
                if output_format == 0:  # XML
                    self.generate_xml(palettes, output_file, feedback)
                elif output_format == 1:  # GPL
                    self.generate_gpl(palettes[0], output_file, feedback)
                else:  # Both
                    xml_file = output_file.rsplit('.', 1)[0] + '.xml'
                    gpl_file = output_file.rsplit('.', 1)[0] + '.gpl'
                    self.generate_xml(palettes, xml_file, feedback)
                    self.generate_gpl(palettes[0], gpl_file, feedback)

            feedback.pushInfo('✓ Palette generation complete!')
            
        except Exception as e:
            feedback.reportError(f'Error generating output: {str(e)}')
            return {}

        return {self.OUTPUT_FILE: output_file if output_mode == 1 else 'Imported to QGIS'}

    def import_to_qgis(self, palettes, feedback):
        """Import color palettes directly into QGIS Style Manager"""
        style = QgsStyle.defaultStyle()
        
        for palette in palettes:
            name = palette['name']
            tags = palette['tags']
            colors = palette['colors']
            
            # Check if palette already exists
            if style.colorRampNames() and name in style.colorRampNames():
                feedback.pushInfo(f'⚠ Palette "{name}" already exists, skipping...')
                continue
            
            # Create gradient color ramp with stops
            color_ramp = QgsGradientColorRamp()
            
            if len(colors) >= 2:
                # Set start and end colors
                start_color = QColor(colors[0]['r'], colors[0]['g'], colors[0]['b'], colors[0]['a'])
                end_color = QColor(colors[-1]['r'], colors[-1]['g'], colors[-1]['b'], colors[-1]['a'])
                color_ramp.setColor1(start_color)
                color_ramp.setColor2(end_color)
                
                # Add intermediate stops
                if len(colors) > 2:
                    stops = []
                    for i in range(1, len(colors) - 1):
                        offset = i / (len(colors) - 1)
                        color = QColor(colors[i]['r'], colors[i]['g'], colors[i]['b'], colors[i]['a'])
                        stops.append(QgsGradientStop(offset, color))
                    color_ramp.setStops(stops)
            elif len(colors) == 1:
                # Single color - create monochrome ramp
                color = QColor(colors[0]['r'], colors[0]['g'], colors[0]['b'], colors[0]['a'])
                color_ramp.setColor1(color)
                color_ramp.setColor2(color)
            
            # Add to QGIS style
            tag_list = [tag.strip() for tag in tags.split(',')]
            if style.addColorRamp(name, color_ramp, True):
                # Add tags
                for tag in tag_list:
                    if tag:
                        style.tagSymbol(QgsStyle.ColorrampEntity, name, [tag])
                feedback.pushInfo(f'✓ Imported palette "{name}" to QGIS')
            else:
                feedback.reportError(f'Failed to import palette "{name}"')

    def read_csv_palettes(self, csv_file, feedback):
        palettes = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            header = [h.strip().lower() for h in header]
            
            name_idx = next((i for i, h in enumerate(header) if h in ['palette', 'name']), 0)
            tags_idx = next((i for i, h in enumerate(header) if h == 'tags'), -1)
            
            for row in reader:
                if not row or not row[name_idx].strip():
                    continue
                
                name = row[name_idx].strip()
                tags = row[tags_idx].strip() if tags_idx >= 0 and tags_idx < len(row) else name.lower()
                
                color_values = [row[i].strip() for i in range(len(row)) 
                               if i != name_idx and i != tags_idx and i < len(row) and row[i].strip()]
                
                colors = self.parse_hex_colors(','.join(color_values), feedback)
                
                if colors:
                    palettes.append({
                        'name': name,
                        'tags': tags,
                        'colors': colors
                    })
        
        return palettes

    def parse_hex_colors(self, color_string, feedback):
        hex_colors = [c.strip() for c in color_string.split(',') if c.strip()]
        valid_colors = []
        
        for hex_color in hex_colors:
            rgba = self.hex_to_rgba(hex_color)
            if rgba:
                valid_colors.append(rgba)
            else:
                feedback.pushInfo(f'⚠ Invalid hex color: {hex_color}')
        
        return valid_colors

    def hex_to_rgba(self, hex_str):
        # Validate hex format
        if not re.match(r'^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$', hex_str):
            return None
        
        hex_str = hex_str.lstrip('#')
        
        # Expand shorthand
        if len(hex_str) == 3:  # RGB
            hex_str = ''.join([c*2 for c in hex_str])
        elif len(hex_str) == 4:  # RGBA
            hex_str = ''.join([c*2 for c in hex_str])
        
        # Parse values
        if len(hex_str) == 8:  # RRGGBBAA
            return {
                'r': int(hex_str[0:2], 16),
                'g': int(hex_str[2:4], 16),
                'b': int(hex_str[4:6], 16),
                'a': int(hex_str[6:8], 16)
            }
        else:  # RRGGBB
            return {
                'r': int(hex_str[0:2], 16),
                'g': int(hex_str[2:4], 16),
                'b': int(hex_str[4:6], 16),
                'a': 255
            }

    def generate_xml(self, palettes, output_file, feedback):
        xml_content = '<!DOCTYPE qgis_style>\n<qgis_style version="2">\n<symbols/>\n<colorramps>\n'
        
        for palette in palettes:
            name = palette['name']
            tags = palette['tags']
            colors = palette['colors']
            
            xml_content += f'<colorramp type="preset" name="{name}" tags="{tags}">\n  <Option type="Map">\n'
            
            for i, color in enumerate(colors):
                rgba_str = f"{color['r']},{color['g']},{color['b']},{color['a']}"
                xml_content += f'    <Option type="QString" name="preset_color_{i}" value="{rgba_str}"/>\n'
            
            xml_content += '    <Option type="QString" name="rampType" value="preset"/>\n  </Option>\n</colorramp>\n'
        
        xml_content += '</colorramps>\n<textformats/>\n<labelsettings/>\n<legendpatchshapes/>\n<symbols3d/>\n</qgis_style>'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        feedback.pushInfo(f'✓ XML file saved: {output_file}')

    def generate_gpl(self, palette, output_file, feedback):
        gpl_content = "GIMP Palette\n"
        gpl_content += f"Name: {palette['name']}\n"
        gpl_content += "Columns: 8\n#\n"
        
        for color in palette['colors']:
            r, g, b = color['r'], color['g'], color['b']
            color_name = self.get_closest_color_name(r, g, b)
            gpl_content += f"{str(r).rjust(3)} {str(g).rjust(3)} {str(b).rjust(3)}\t{color_name}\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(gpl_content)
        
        feedback.pushInfo(f'✓ GPL file saved: {output_file}')

    def get_closest_color_name(self, r, g, b):
        # Simplified color name mapping
        color_names = {
            (0, 0, 0): 'Black', (255, 255, 255): 'White',
            (255, 0, 0): 'Red', (0, 255, 0): 'Green', (0, 0, 255): 'Blue',
            (255, 255, 0): 'Yellow', (255, 0, 255): 'Magenta', (0, 255, 255): 'Cyan',
            (128, 128, 128): 'Gray', (255, 165, 0): 'Orange', (128, 0, 128): 'Purple'
        }
        
        min_dist = float('inf')
        closest_name = "Custom Color"
        
        for (cr, cg, cb), name in color_names.items():
            dist = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
            if dist < min_dist:
                min_dist = dist
                closest_name = name
        
        return closest_name
