from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, 
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterString,
                       QgsProcessingException)
import numpy as np
from osgeo import gdal
import processing

class DEMReclassifyAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    BANDS = 'BANDS'
    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                'Input DEM',
                [QgsProcessing.TypeRaster]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterString(
                self.BANDS,
                'Elevation Bands (leave empty for default)',
                defaultValue='',
                optional=True,
                multiLine=False
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                'Output Reclassified DEM'
            )
        )
    
    def name(self):
        return 'dem_reclassify_elevation_bands'
    
    def displayName(self):
        return 'DEM Reclassify to Elevation Bands'
    
    def group(self):
        return 'Raster Tools'
    
    def groupId(self):
        return 'raster_tools'
    
    def shortHelpString(self):
        return """Reclassify a DEM into elevation bands.
        
        Default bands: 0-100, 100-200, 200-500, 500-1000, 1000-1500, 1500-2000, 2000-3000, 3000-4000, 4000+
        
        Custom format: Enter bands as comma-separated ranges, e.g.:
        0-100, 100-200, 200-500, 500-1000, 1000+
        
        Or with semicolons:
        0-100; 100-200; 200-500; 500-1000; 1000+
        
        Use '+' or 'inf' for the upper bound of the last band.
        Each band will be assigned a sequential class value (1, 2, 3, etc.)"""
    
    def parse_bands(self, bands_string):
        """Parse the bands string into a list of (min, max, class_val) tuples."""
        if not bands_string or bands_string.strip() == '':
            # Default bands
            return [
                (0, 100, 1),
                (100, 200, 2),
                (200, 500, 3),
                (500, 1000, 4),
                (1000, 1500, 5),
                (1500, 2000, 6),
                (2000, 3000, 7),
                (3000, 4000, 8),
                (4000, np.inf, 9)
            ]
        
        # Parse custom bands
        bands = []
        # Split by comma or semicolon
        parts = bands_string.replace(';', ',').split(',')
        
        class_val = 1
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Split by dash
            if '-' in part:
                range_parts = part.split('-')
                min_val = float(range_parts[0].strip())
                max_str = range_parts[1].strip()
                
                # Handle inf, +, or numeric value
                if max_str in ['+', 'inf', 'infinity']:
                    max_val = np.inf
                else:
                    max_val = float(max_str)
            elif '+' in part:
                # Format like "1000+"
                min_val = float(part.replace('+', '').strip())
                max_val = np.inf
            else:
                raise ValueError(f"Invalid band format: {part}. Use format like '0-100' or '1000+'")
            
            bands.append((min_val, max_val, class_val))
            class_val += 1
        
        return bands
    
    def processAlgorithm(self, parameters, context, feedback):
        # Get the source file path (thread-safe)
        source = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException('Invalid input raster layer')
        
        dem_source = source.source()
        bands_string = self.parameterAsString(parameters, self.BANDS, context)
        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        
        # Parse elevation bands
        try:
            bands = self.parse_bands(bands_string)
            feedback.pushInfo(f'Using {len(bands)} elevation bands:')
            for min_val, max_val, class_val in bands:
                if max_val == np.inf:
                    feedback.pushInfo(f'  Class {class_val}: {min_val}+')
                else:
                    feedback.pushInfo(f'  Class {class_val}: {min_val}-{max_val}')
        except Exception as e:
            raise QgsProcessingException(f"Error parsing bands: {str(e)}")
        
        # Open with GDAL
        src_ds = gdal.Open(dem_source, gdal.GA_ReadOnly)
        if src_ds is None:
            raise QgsProcessingException(f"Could not open raster: {dem_source}")
        
        try:
            band = src_ds.GetRasterBand(1)
            if band is None:
                raise QgsProcessingException("Could not access raster band")
            
            # Get raster properties
            x_size = src_ds.RasterXSize
            y_size = src_ds.RasterYSize
            gt = src_ds.GetGeoTransform()
            proj = src_ds.GetProjection()
            nodata_value = band.GetNoDataValue()
            
            feedback.pushInfo(f'Reading DEM data ({x_size} x {y_size})...')
            
            # Read array
            arr = band.ReadAsArray()
            if arr is None:
                raise QgsProcessingException("Could not read raster data")
            
            # Create output array
            output_arr = np.zeros_like(arr, dtype=np.uint16)
            
            # Handle nodata before reclassification
            if nodata_value is not None:
                nodata_mask = (arr == nodata_value)
            else:
                # Try to get mask band
                mask_band = band.GetMaskBand()
                if mask_band is not None:
                    mask_arr = mask_band.ReadAsArray()
                    nodata_mask = (mask_arr == 0)
                else:
                    nodata_mask = np.zeros_like(arr, dtype=bool)
            
            # Reclassify
            total = len(bands)
            for idx, (min_val, max_val, class_val) in enumerate(bands):
                if feedback.isCanceled():
                    break
                
                progress = int((idx / total) * 100)
                feedback.setProgress(progress)
                
                if max_val == np.inf:
                    feedback.pushInfo(f'Processing band {idx+1}/{total}: {min_val}+')
                    mask = (arr >= min_val) & (~nodata_mask)
                else:
                    feedback.pushInfo(f'Processing band {idx+1}/{total}: {min_val}-{max_val}')
                    mask = (arr >= min_val) & (arr < max_val) & (~nodata_mask)
                
                output_arr[mask] = class_val
            
            # Set nodata pixels to 0
            output_arr[nodata_mask] = 0
            
        finally:
            # Close source dataset
            src_ds = None
        
        # Create output raster
        feedback.pushInfo('Writing output raster...')
        driver = gdal.GetDriverByName('GTiff')
        dst_ds = driver.Create(
            output_path,
            x_size,
            y_size,
            1,
            gdal.GDT_UInt16,
            options=['COMPRESS=LZW']
        )
        
        if dst_ds is None:
            raise QgsProcessingException(f"Could not create output raster: {output_path}")
        
        try:
            dst_ds.SetGeoTransform(gt)
            dst_ds.SetProjection(proj)
            
            dst_band = dst_ds.GetRasterBand(1)
            dst_band.WriteArray(output_arr)
            dst_band.SetNoDataValue(0)
            dst_band.FlushCache()
            
            # Set color interpretation
            dst_band.SetColorInterpretation(gdal.GCI_GrayIndex)
            
        finally:
            # Close output dataset
            dst_ds = None
        
        feedback.setProgress(100)
        feedback.pushInfo('DEM reclassification complete!')
        
        return {self.OUTPUT: output_path}

    def createInstance(self):
        return DEMReclassifyAlgorithm()
