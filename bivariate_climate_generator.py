## Bivariate Climate Generator (Quantile-based)
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterBoolean, QgsProcessingParameterCrs,
                       QgsProcessingParameterNumber, QgsProcessingParameterRasterDestination)
import processing
from osgeo import gdal
import numpy as np
import os, tempfile


# ---------- Calculator helpers ----------
def _calc_qgis(expr, layers, out_path):
    params = {'EXPRESSION': expr, 'LAYERS': layers, 'CRS': None, 'OUTPUT': out_path}
    return processing.run('qgis:rastercalculator', params)

def _calc_gdal(expr, layer_A, layer_B, out_path, rtype=5):
    params = {
        'INPUT_A': layer_A, 'BAND_A': 1,
        'INPUT_B': layer_B, 'BAND_B': 1,
        'FORMULA': expr,
        'NO_DATA': None, 'RTYPE': rtype, 'OPTIONS': '', 'EXTRA': '',
        'OUTPUT': out_path
    }
    return processing.run('gdal:rastercalculator', params)

def _runcalc_dual(qgis_expr, gdal_expr, layers, out_path, feedback):
    try:
        return _calc_qgis(qgis_expr, layers, out_path)
    except Exception as e_qgis:
        A = layers[0]; B = layers[1] if len(layers) > 1 else layers[0]
        try:
            return _calc_gdal(gdal_expr, A, B, out_path)
        except Exception as e_gdal:
            raise RuntimeError(f"Raster calculator failed:\nQGIS: {e_qgis}\nGDAL: {e_gdal}")


# ---------- Algorithm ----------
class BivariateClimateGenerator(QgsProcessingAlgorithm):
    RASTER_A, RASTER_B = 'RASTER_A', 'RASTER_B'
    TARGET_CRS, DO_REPROJECT_ALIGN = 'TARGET_CRS', 'DO_REPROJECT_ALIGN'
    APPLY_DIVISOR_B, DIVISOR_B = 'APPLY_DIVISOR_B', 'DIVISOR_B'
    OUT_A_CLASS, OUT_B_CLASS, OUT_BIVAR = 'OUT_A_CLASS', 'OUT_B_CLASS', 'OUT_BIVAR'

    def tr(self, text): return QCoreApplication.translate('BivariateClimateGenerator', text)
    def createInstance(self): return BivariateClimateGenerator()
    def name(self): return 'bivariate_climate_generator'
    def displayName(self): return self.tr('Bivariate Climate Generator')
    def group(self): return self.tr('Raster – Bivariate')
    def groupId(self): return 'raster_bivariate'
    def shortHelpString(self):
        return self.tr(
            'Generates 3-quantile climate classes (Low/Medium/High) for two rasters and '
            'combines them into a 2-digit bivariate code (11–33). '
            'Automatically aligns rasters and supports optional division of Raster B '
            '(e.g. to convert totals to averages).'
        )

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.RASTER_A, self.tr('Raster A (e.g. Temperature)')))
        self.addParameter(QgsProcessingParameterRasterLayer(self.RASTER_B, self.tr('Raster B (e.g. Precipitation)')))
        self.addParameter(QgsProcessingParameterBoolean(self.DO_REPROJECT_ALIGN,
            self.tr('Reproject & align rasters to Raster A grid?'), defaultValue=True))
        self.addParameter(QgsProcessingParameterCrs(self.TARGET_CRS,
            self.tr('Target CRS (optional, e.g. EPSG:21037)'), optional=True))
        self.addParameter(QgsProcessingParameterBoolean(self.APPLY_DIVISOR_B,
            self.tr('Divide Raster B by factor before processing?'), defaultValue=False))
        self.addParameter(QgsProcessingParameterNumber(self.DIVISOR_B,
            self.tr('Division factor for Raster B (e.g. 30 for monthly average)'),
            type=QgsProcessingParameterNumber.Double, defaultValue=30.0, minValue=1e-6))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUT_A_CLASS,
            self.tr('Output: Raster A class (1–3) [GeoTIFF]')))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUT_B_CLASS,
            self.tr('Output: Raster B class (1–3) [GeoTIFF]')))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUT_BIVAR,
            self.tr('Output: Bivariate code (11–33) [GeoTIFF]')))

    def processAlgorithm(self, parameters, context, feedback):
        raster_a = self.parameterAsRasterLayer(parameters, self.RASTER_A, context)
        raster_b = self.parameterAsRasterLayer(parameters, self.RASTER_B, context)
        do_align = self.parameterAsBoolean(parameters, self.DO_REPROJECT_ALIGN, context)
        target_crs = self.parameterAsCrs(parameters, self.TARGET_CRS, context)
        apply_div_b = self.parameterAsBoolean(parameters, self.APPLY_DIVISOR_B, context)
        divisor_b = self.parameterAsDouble(parameters, self.DIVISOR_B, context)
        out_a_class = self.parameterAsOutputLayer(parameters, self.OUT_A_CLASS, context)
        out_b_class = self.parameterAsOutputLayer(parameters, self.OUT_B_CLASS, context)
        out_bivar = self.parameterAsOutputLayer(parameters, self.OUT_BIVAR, context)
        tmpdir = tempfile.mkdtemp(prefix='bivar_')

        # ---- Reproject & Align ----
        def warp_to_match(src, dst, ref, t_srs):
            ref_ds = gdal.Open(ref)
            gt = ref_ds.GetGeoTransform()
            px, py = abs(gt[1]), abs(gt[5])
            minx, maxy = gt[0], gt[3]
            cols, rows = ref_ds.RasterXSize, ref_ds.RasterYSize
            maxx, miny = minx + cols * px, maxy - rows * py
            te = [minx, miny, maxx, maxy]
            args = {
                'INPUT': src, 'SOURCE_CRS': None,
                'TARGET_CRS': t_srs if t_srs else None,
                'RESAMPLING': 1, 'DATA_TYPE': 5,
                'TARGET_EXTENT': te,
                'TARGET_EXTENT_CRS': t_srs.authid() if t_srs else ref_ds.GetProjection(),
                'X_RESOLUTION': px, 'Y_RESOLUTION': py,
                'MULTITHREADING': True, 'OUTPUT': dst
            }
            for alg in ('gdal:warpreproject', 'gdal:warp'):
                try: return processing.run(alg, args, context=context, feedback=feedback)
                except Exception: continue
            raise RuntimeError("GDAL warp not available.")

        path_a, path_b = raster_a.source(), raster_b.source()
        if do_align:
            a_ref = os.path.join(tmpdir, 'A_ref.tif')
            if target_crs.isValid(): warp_to_match(path_a, a_ref, path_a, target_crs)
            else: gdal.Translate(a_ref, path_a, format='GTiff')
            a_al = os.path.join(tmpdir, 'A_aligned.tif')
            warp_to_match(a_ref, a_al, a_ref, target_crs if target_crs.isValid() else None)
            b_al = os.path.join(tmpdir, 'B_aligned.tif')
            warp_to_match(path_b, b_al, a_al, target_crs if target_crs.isValid() else None)
        else:
            a_al = os.path.join(tmpdir, 'A_aligned.tif')
            b_al = os.path.join(tmpdir, 'B_aligned.tif')
            gdal.Translate(a_al, path_a, format='GTiff', outputType=gdal.GDT_Float32)
            gdal.Translate(b_al, path_b, format='GTiff', outputType=gdal.GDT_Float32)

        # ---- Optional divide B ----
        b_input = b_al
        if apply_div_b:
            b_scaled = os.path.join(tmpdir, 'B_scaled.tif')
            qgis_expr = f' "B@1" / {divisor_b} '; gdal_expr = f' B / {divisor_b} '
            _runcalc_dual(qgis_expr, gdal_expr, [b_al], b_scaled, feedback)
            b_input = b_scaled

        # ---- Quantiles ----
        def quantiles(path):
            ds = gdal.Open(path); arr = ds.GetRasterBand(1).ReadAsArray().astype('float64')
            nd = ds.GetRasterBand(1).GetNoDataValue()
            if nd is not None: arr = np.where(arr == nd, np.nan, arr)
            vals = arr[~np.isnan(arr)]
            return float(np.percentile(vals, 33.333)), float(np.percentile(vals, 66.667))
        a_q1,a_q2 = quantiles(a_al); b_q1,b_q2 = quantiles(b_input)

        # ---- Reclassify ----
        qa = f'( "A@1" <= {a_q1} ) * 1 + ( ( "A@1" > {a_q1} ) AND ( "A@1" <= {a_q2} ) ) * 2 + ( "A@1" > {a_q2} ) * 3'
        ga = f'(A <= {a_q1}) * 1 + ((A > {a_q1}) * (A <= {a_q2})) * 2 + (A > {a_q2}) * 3'
        _runcalc_dual(qa, ga, [a_al], out_a_class, feedback)

        qb = f'( "B@1" <= {b_q1} ) * 1 + ( ( "B@1" > {b_q1} ) AND ( "B@1" <= {b_q2} ) ) * 2 + ( "B@1" > {b_q2} ) * 3'
        gb = f'(B <= {b_q1}) * 1 + ((B > {b_q1}) * (B <= {b_q2})) * 2 + (B > {b_q2}) * 3'
        _runcalc_dual(qb, gb, [b_input], out_b_class, feedback)

        # ---- Combine ----
        q_ab = '( "A@1" * 10 ) + "B@1"'; g_ab = '(A * 10) + B'
        _runcalc_dual(q_ab, g_ab, [out_a_class, out_b_class], out_bivar, feedback)

        feedback.pushInfo(f'Terciles A: q1={a_q1:.4f}, q2={a_q2:.4f}')
        feedback.pushInfo(f'Terciles B: q1={b_q1:.4f}, q2={b_q2:.4f}')
        return {self.OUT_A_CLASS: out_a_class, self.OUT_B_CLASS: out_b_class, self.OUT_BIVAR: out_bivar}

def classFactory(iface=None): return BivariateClimateGenerator()
