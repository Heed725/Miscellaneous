from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsSymbol,
                       QgsCategorizedSymbolRenderer,
                       QgsRendererCategory)
from qgis.PyQt.QtGui import QColor
import random
import colorsys

class CategorizeByColorAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    FIELD = 'FIELD'
    COLOR_MODE = 'COLOR_MODE'
    HUE_START = 'HUE_START'
    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                'Input layer',
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                'Field to categorize',
                parentLayerParameterName=self.INPUT
            )
        )
        
        self.addParameter(
            QgsProcessingParameterEnum(
                self.COLOR_MODE,
                'Color mode',
                options=[
                    'Random Colors', 
                    'Rainbow Spectrum', 
                    'Red Hues', 
                    'Orange Hues',
                    'Yellow Hues',
                    'Green Hues', 
                    'Cyan Hues',
                    'Blue Hues',
                    'Purple Hues',
                    'Magenta Hues',
                    'Warm Colors (Red-Yellow)',
                    'Cool Colors (Green-Blue)',
                    'Earth Tones (Brown-Green)',
                    'Pastel Colors',
                    'Vibrant Colors',
                    'Monochrome (Grayscale)',
                    'Ocean Colors (Blue-Green)',
                    'Forest Colors (Green Variants)',
                    'Sunset Colors (Orange-Purple)',
                    'Desert Colors (Tan-Orange)',
                    'Neon Colors',
                    'Dark Mode Colors',
                    'Autumn Colors (Red-Orange-Brown)',
                    'Spring Colors (Light Green-Pink)',
                    'Winter Colors (Blue-White-Gray)'
                ],
                defaultValue=0
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.HUE_START,
                'Hue start (0-360, for hue modes)',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=0,
                minValue=0,
                maxValue=360,
                optional=True
            )
        )
    
    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        field_name = self.parameterAsString(parameters, self.FIELD, context)
        color_mode = self.parameterAsEnum(parameters, self.COLOR_MODE, context)
        hue_start = self.parameterAsInt(parameters, self.HUE_START, context)
        
        # Get unique values from the field
        field_index = layer.fields().indexFromName(field_name)
        unique_values = layer.uniqueValues(field_index)
        
        feedback.pushInfo(f'Found {len(unique_values)} unique values')
        
        # Create categories
        categories = []
        
        for i, value in enumerate(sorted(unique_values)):
            # Generate color based on mode
            if color_mode == 0:  # Random
                color = self.get_random_color()
            elif color_mode == 1:  # Rainbow Spectrum
                color = self.get_hue_color(i, len(unique_values), hue_start, 1.0)
            elif color_mode == 2:  # Red hues (0°)
                color = self.get_hue_color(i, len(unique_values), 0, 0.15)
            elif color_mode == 3:  # Orange hues (30°)
                color = self.get_hue_color(i, len(unique_values), 30, 0.15)
            elif color_mode == 4:  # Yellow hues (60°)
                color = self.get_hue_color(i, len(unique_values), 60, 0.15)
            elif color_mode == 5:  # Green hues (120°)
                color = self.get_hue_color(i, len(unique_values), 120, 0.15)
            elif color_mode == 6:  # Cyan hues (180°)
                color = self.get_hue_color(i, len(unique_values), 180, 0.15)
            elif color_mode == 7:  # Blue hues (240°)
                color = self.get_hue_color(i, len(unique_values), 240, 0.15)
            elif color_mode == 8:  # Purple hues (270°)
                color = self.get_hue_color(i, len(unique_values), 270, 0.15)
            elif color_mode == 9:  # Magenta hues (300°)
                color = self.get_hue_color(i, len(unique_values), 300, 0.15)
            elif color_mode == 10:  # Warm colors (0-60°)
                color = self.get_warm_color(i, len(unique_values))
            elif color_mode == 11:  # Cool colors (120-240°)
                color = self.get_cool_color(i, len(unique_values))
            elif color_mode == 12:  # Earth tones
                color = self.get_earth_tone(i, len(unique_values))
            elif color_mode == 13:  # Pastel colors
                color = self.get_pastel_color(i, len(unique_values))
            elif color_mode == 14:  # Vibrant colors
                color = self.get_vibrant_color(i, len(unique_values))
            elif color_mode == 15:  # Monochrome
                color = self.get_monochrome_color(i, len(unique_values))
            elif color_mode == 16:  # Ocean colors
                color = self.get_ocean_color(i, len(unique_values))
            elif color_mode == 17:  # Forest colors
                color = self.get_forest_color(i, len(unique_values))
            elif color_mode == 18:  # Sunset colors
                color = self.get_sunset_color(i, len(unique_values))
            elif color_mode == 19:  # Desert colors
                color = self.get_desert_color(i, len(unique_values))
            elif color_mode == 20:  # Neon colors
                color = self.get_neon_color(i, len(unique_values))
            elif color_mode == 21:  # Dark mode colors
                color = self.get_dark_mode_color(i, len(unique_values))
            elif color_mode == 22:  # Autumn colors
                color = self.get_autumn_color(i, len(unique_values))
            elif color_mode == 23:  # Spring colors
                color = self.get_spring_color(i, len(unique_values))
            elif color_mode == 24:  # Winter colors
                color = self.get_winter_color(i, len(unique_values))
            
            # Create symbol
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            symbol.setColor(color)
            
            # Create category
            category = QgsRendererCategory(value, symbol, str(value))
            categories.append(category)
        
        # Apply categorized renderer
        renderer = QgsCategorizedSymbolRenderer(field_name, categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        
        feedback.pushInfo('Categorization complete!')
        
        return {}
    
    def get_random_color(self):
        """Generate a random color"""
        return QColor(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
    
    def get_hue_color(self, index, total, base_hue, hue_range):
        """Generate color based on hue
        
        Args:
            index: Current category index
            total: Total number of categories
            base_hue: Base hue (0-360)
            hue_range: Range of hues to use (0-1, where 1 is full spectrum)
        """
        if total == 1:
            hue = base_hue / 360.0
        else:
            # Distribute colors across the hue range
            hue_offset = (index / (total - 1)) * hue_range * 360
            hue = ((base_hue + hue_offset) % 360) / 360.0
        
        # Convert HSV to RGB
        saturation = 0.7 + random.random() * 0.3  # 0.7-1.0
        value = 0.8 + random.random() * 0.2  # 0.8-1.0
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_warm_color(self, index, total):
        """Generate warm colors (red to yellow range)"""
        if total == 1:
            hue = 30 / 360.0
        else:
            hue = (index / (total - 1)) * 60 / 360.0  # 0-60 degrees
        
        saturation = 0.7 + random.random() * 0.3
        value = 0.8 + random.random() * 0.2
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_cool_color(self, index, total):
        """Generate cool colors (green to blue range)"""
        if total == 1:
            hue = 180 / 360.0
        else:
            hue = (120 + (index / (total - 1)) * 120) / 360.0  # 120-240 degrees
        
        saturation = 0.7 + random.random() * 0.3
        value = 0.8 + random.random() * 0.2
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_earth_tone(self, index, total):
        """Generate earth tones (browns, greens, tans)"""
        # Earth tones: mix of browns (30-60 hue) and greens (80-140 hue)
        if total == 1:
            hue = 30 / 360.0
        else:
            # Alternate between brown and green ranges
            if index % 2 == 0:
                hue = (30 + (index / total) * 30) / 360.0
            else:
                hue = (80 + (index / total) * 60) / 360.0
        
        saturation = 0.3 + random.random() * 0.4  # Lower saturation for earth tones
        value = 0.4 + random.random() * 0.4
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_pastel_color(self, index, total):
        """Generate pastel colors (low saturation, high value)"""
        if total == 1:
            hue = 0.0
        else:
            hue = index / total  # Full spectrum
        
        saturation = 0.25 + random.random() * 0.25  # Low saturation
        value = 0.85 + random.random() * 0.15  # High value
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_vibrant_color(self, index, total):
        """Generate vibrant colors (high saturation)"""
        if total == 1:
            hue = 0.0
        else:
            hue = index / total  # Full spectrum
        
        saturation = 0.85 + random.random() * 0.15  # High saturation
        value = 0.85 + random.random() * 0.15  # High value
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_monochrome_color(self, index, total):
        """Generate grayscale colors"""
        if total == 1:
            gray = 128
        else:
            # Distribute from dark to light
            gray = int(50 + (index / (total - 1)) * 180)
        
        return QColor(gray, gray, gray)
    
    def get_ocean_color(self, index, total):
        """Generate ocean colors (blue to green-blue)"""
        if total == 1:
            hue = 200 / 360.0
        else:
            hue = (180 + (index / (total - 1)) * 60) / 360.0  # 180-240 degrees
        
        saturation = 0.5 + random.random() * 0.4
        value = 0.5 + random.random() * 0.4
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_forest_color(self, index, total):
        """Generate forest colors (various greens)"""
        if total == 1:
            hue = 120 / 360.0
        else:
            hue = (90 + (index / (total - 1)) * 80) / 360.0  # 90-170 degrees
        
        saturation = 0.4 + random.random() * 0.5
        value = 0.3 + random.random() * 0.5
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_sunset_color(self, index, total):
        """Generate sunset colors (orange to purple)"""
        if total == 1:
            hue = 30 / 360.0
        else:
            # Blend from orange (30) to purple (280)
            hue = (30 + (index / (total - 1)) * 250) / 360.0
        
        saturation = 0.7 + random.random() * 0.3
        value = 0.7 + random.random() * 0.3
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_desert_color(self, index, total):
        """Generate desert colors (tan, sand, orange)"""
        if total == 1:
            hue = 40 / 360.0
        else:
            hue = (25 + (index / (total - 1)) * 35) / 360.0  # 25-60 degrees
        
        saturation = 0.3 + random.random() * 0.4  # Medium saturation
        value = 0.6 + random.random() * 0.3  # Medium-high brightness
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_neon_color(self, index, total):
        """Generate neon/fluorescent colors"""
        if total == 1:
            hue = 0.0
        else:
            hue = index / total  # Full spectrum
        
        saturation = 1.0  # Maximum saturation
        value = 1.0  # Maximum brightness
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_dark_mode_color(self, index, total):
        """Generate dark mode friendly colors (muted, dark)"""
        if total == 1:
            hue = 0.0
        else:
            hue = index / total  # Full spectrum
        
        saturation = 0.5 + random.random() * 0.3
        value = 0.4 + random.random() * 0.3  # Keep values low for dark mode
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_autumn_color(self, index, total):
        """Generate autumn colors (red, orange, brown)"""
        if total == 1:
            hue = 30 / 360.0
        else:
            # Cycle through red (0), orange (30), brown (40)
            hue_options = [0, 15, 30, 40, 20]
            hue = (hue_options[index % len(hue_options)] + (index / total) * 10) / 360.0
        
        saturation = 0.5 + random.random() * 0.4
        value = 0.5 + random.random() * 0.4
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_spring_color(self, index, total):
        """Generate spring colors (light green, pink, yellow)"""
        if total == 1:
            hue = 120 / 360.0
        else:
            # Cycle through light greens, pinks, yellows
            hue_options = [100, 120, 140, 320, 340, 60]
            hue = hue_options[index % len(hue_options)] / 360.0
        
        saturation = 0.3 + random.random() * 0.3  # Light saturation
        value = 0.8 + random.random() * 0.2  # High brightness
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def get_winter_color(self, index, total):
        """Generate winter colors (blue, white, gray)"""
        if total == 1:
            hue = 210 / 360.0
        else:
            hue = (200 + (index / (total - 1)) * 40) / 360.0  # 200-240 degrees (blues)
        
        saturation = 0.1 + random.random() * 0.3  # Low saturation (icy)
        value = 0.7 + random.random() * 0.3  # High brightness (snowy)
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return QColor(int(r * 255), int(g * 255), int(b * 255))
    
    def name(self):
        return 'categorizebycolor'
    
    def displayName(self):
        return 'Categorize by Color'
    
    def group(self):
        return 'Styling'
    
    def groupId(self):
        return 'styling'
    
    def createInstance(self):
        return CategorizeByColorAlgorithm()
    
    def shortHelpString(self):
        return """
        Categorizes a vector layer based on a field and applies colors.
        
        Color Mode Options (25 choices):
        
        Basic Modes:
        - Random Colors: Each category gets a random color
        - Rainbow Spectrum: Full color spectrum distribution
        
        Single Hue Variations:
        - Red/Orange/Yellow/Green/Cyan/Blue/Purple/Magenta Hues: Variations of specific colors
        
        Temperature & Range:
        - Warm Colors: Red to yellow range (0-60°)
        - Cool Colors: Green to blue range (120-240°)
        
        Natural Themes:
        - Earth Tones: Browns, greens, and natural colors
        - Ocean Colors: Blue to green-blue (water features)
        - Forest Colors: Various shades of green (vegetation)
        - Desert Colors: Tan, sand, orange (arid landscapes)
        
        Seasonal Palettes:
        - Autumn Colors: Red, orange, brown (fall foliage)
        - Spring Colors: Light green, pink, yellow (fresh growth)
        - Winter Colors: Blue, white, gray (ice and snow)
        
        Artistic Styles:
        - Pastel Colors: Soft, light colors with low saturation
        - Vibrant Colors: Bright, highly saturated colors
        - Neon Colors: Fluorescent, maximum brightness
        - Dark Mode Colors: Muted colors for dark backgrounds
        - Sunset Colors: Orange to purple gradient
        
        Grayscale:
        - Monochrome: Grayscale from dark to light
        
        The script will:
        1. Find all unique values in the selected field
        2. Generate colors based on the selected mode
        3. Apply categorized symbology to the layer
        """
