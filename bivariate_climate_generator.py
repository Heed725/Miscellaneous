## Bivariate Climate Generator (Quantile-based, paletted QML)
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing, QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer,
    QgsProcessingParameterBoolean, QgsProcessingParameterCrs,
    QgsProcessingParameterNumber, QgsProcessingParameterRasterDestination,
    QgsProcessingParameterFileDestination
)
import processing
from osgeo import gdal
import numpy as np
import os, tempfile


# ---------- Raster calculator helpers ----------
def _calc_qgis(expr, layers, out_path):
    """QGIS raster calculator using QGIS-style band refs ("A@1","B@1")."""
    params = {'EXPRESSION': expr, 'LAYERS': layers, 'CRS': None, 'OUTPUT': out_path}
    return processing.run('qgis:rastercalculator', params)

def _calc_gdal(expr, layer_A, layer_B, out_path, rtype=5):
    """GDAL raster calculator using variables A,B."""
    params = {
        'INPUT_A': layer_A, 'BAND_A': 1,
        'INPUT_B': layer_B, 'BAND_B': 1,
        'INPUT_C': None, 'BAND_C': 1,
        'INPUT_D': None, 'BAND_D': 1,
        'INPUT_E': None, 'BAND_E': 1,
        'INPUT_F': None, 'BAND_F': 1,
        'FORMULA': expr,
        'NO_DATA': None, 'RTYPE': rtype, 'OPTIONS': '', 'EXTRA': '',
        'OUTPUT': out_path
    }
    return processing.run('gdal:rastercalculator', params)

def _runcalc_dual(qgis_expr, gdal_expr, layers, out_path, feedback):
    """Try QGIS calc first; fall back to GDAL calc."""
    try:
        return _calc_qgis(qgis_expr, layers, out_path)
    except Exception as e_qgis:
        A = layers[0]
        B = layers[1] if len(layers) > 1 else layers[0]
        try:
            return _calc_gdal(gdal_expr, A, B, out_path)
        except Exception as e_gdal:
            raise RuntimeError(
                "Raster calculator failed in both QGIS and GDAL.\n"
                f"QGIS error: {e_qgis}\nGDAL error: {e_gdal}"
            )


# ---------- QML writer (PALLETED renderer, with your exact XML structure) ----------
def write_bivariate_qml(qml_path):
    """
    Writes a QGIS paletted raster style (.qml) with the exact structure you provided:
    - DOCTYPE line
    - <rasterrenderer type="paletted">
    - <paletteEntry> items for values 11..33 with your labels and colors
    """
    # EXACT mapping & colors as per your snippet
    items = [
        (11, 'Low Temp, Low Precipitation', '#e8e8e8'),
        (12, 'Low Temp, Medium Precip',     '#dfb0d6'),
        (13, 'Low Temp, High Precip',       '#be64ac'),
        (21, 'Medium Temp, Low Precip',     '#ace4e4'),
        (22, 'Medium Temp, Medium Precip',  '#a5add3'),
        (23, 'Medium Temp, High Precip',    '#8c62aa'),
        (31, 'High Temp, Low Precip',       '#5ac8c8'),
        (32, 'High Temp, Medium Precip',    '#5698b9'),
        (33, 'High Temp, High Precip',      '#3b4994'),
    ]

    doctype = "<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>\n"
    header = (
        '<qgis autoRefreshTime="0" version="3.44.0-Solothurn" '
        'styleCategories="LayerConfiguration|Symbology|MapTips|AttributeTable|Rendering|CustomProperties|Temporal|Elevation|Notes" '
        'maxScale="0" autoRefreshMode="Disabled" hasScaleBasedVisibilityFlag="0" minScale="1e+08">\n'
        '  <flags>\n'
        '    <Identifiable>1</Identifiable>\n'
        '    <Removable>1</Removable>\n'
        '    <Searchable>1</Searchable>\n'
        '    <Private>0</Private>\n'
        '  </flags>\n\n'
        '  <pipe>\n'
        '    <provider>\n'
        '      <resampling zoomedOutResamplingMethod="nearestNeighbour" enabled="false" '
        'zoomedInResamplingMethod="nearestNeighbour" maxOversampling="2"/>\n'
        '    </provider>\n'
        '    <rasterrenderer opacity="1" band="1" type="paletted" alphaBand="-1" nodataColor="">\n'
        '      <rasterTransparency/>\n'
        '      <colorPalette>\n'
    )

    body = ''.join(
        f'        <paletteEntry alpha="255" label="{label}" color="{hexcolor}" value="{val}"/>\n'
        for (val, label, hexcolor) in items
    )

    footer = (
        '      </colorPalette>\n\n'
        '      <colorramp type="cpt-city" name="stevens.pinkblue">\n'
        '        <Option type="Map">\n'
        '          <Option type="QString" name="schemeName" value="cpt-city"/>\n'
        '          <Option type="QString" name="variantName" value="stevens.pinkblue"/>\n'
        '        </Option>\n'
        '      </colorramp>\n'
        '    </rasterrenderer>\n'
        '    <brightnesscontrast brightness="0" contrast="0" gamma="1"/>\n'
        '    <rasterresampler maxOversampling="2"/>\n'
        '  </pipe>\n'
        '  <blendMode>0</blendMode>\n'
        '</qgis>\n'
    )

    with open(qml_path, 'w', encoding='utf-8') as f:
        f.write(doctype + header + body + footer)
    return qml_path


# ---------- Processing Algorithm ----------
class BivariateClimateGenerator(QgsProcessingAlgorithm):
    # Params
    RASTER_A, RASTER_B = 'RASTER_A', 'RASTER_B'
    TARGET_CRS, DO_REPROJECT_ALIGN = 'TARGET_CRS', 'DO_REPROJECT_ALIGN'
    APPLY_DIVISOR_B, DIVISOR_B = 'APPLY_DIVISOR_B', 'DIVISOR_B'
    OUT_A_CLASS, OUT_B_CLASS, OUT_BIVAR = 'OUT_A_CLASS', 'OUT_B_CLASS', 'OUT_BIVAR'
    OUT_QML = 'OUT_QML'

    def tr(self, text): return QCoreApplication.translate('BivariateClimateGenerator', text)
    def createInstance(self): return BivariateClimateGenerator()
    def name(self): return 'bivariate_climate_generator'
    def displayName(self): return self.tr('Bivariate Climate Generator')
    def group(self): return self.tr('Raster – Bivariate')
    def groupId(self): return 'raster_bivariate'
    def shortHelpString(self):
        return self.tr(
            'Generates 3-quantile classes (1/2/3) for two rasters and combines them into 11–33. '
            'Optionally divides Raster B (e.g., /30) and aligns CRS/grid. '
            'Writes a paletted .QML with your 11–33 color mapping and tries to auto-apply it.'
        )

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.RASTER_A, self.tr('Raster A (e.g. Temperature)')))
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.RASTER_B, self.tr('Raster B (e.g. Precipitation)')))

        self.addParameter(QgsProcessingParameterBoolean(
            self.DO_REPROJECT_ALIGN, self.tr('Reproject & align to Raster A grid?'), defaultValue=True))

        self.addParameter(QgsProcessingParameterCrs(
            self.TARGET_CRS, self.tr('Target CRS (optional, e.g. EPSG:21037)'), optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            self.APPLY_DIVISOR_B, self.tr('Divide Raster B by factor before processing?'),
            defaultValue=False))

        self.addParameter(QgsProcessingParameterNumber(
            self.DIVISOR_B, self.tr('Division factor for Raster B (e.g. 30 for monthly average)'),
            type=QgsProcessingParameterNumber.Double, defaultValue=30.0, minValue=1e-6))

        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUT_A_CLASS, self.tr('Output: Raster A class (1–3) [GeoTIFF]')))

        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUT_B_CLASS, self.tr('Output: Raster B class (1–3) [GeoTIFF]')))

        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUT_BIVAR, self.tr('Output: Bivariate code (11–33) [GeoTIFF]')))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUT_QML, self.tr('Output: QML style (optional)'), 'QML files (*.qml)', optional=True))

    def processAlgorithm(self, parameters, context, feedback):
        # Inputs
        raster_a = self.parameterAsRasterLayer(parameters, self.RASTER_A, context)
        raster_b = self.parameterAsRasterLayer(parameters, self.RASTER_B, context)
        do_align = self.parameterAsBoolean(parameters, self.DO_REPROJECT_ALIGN, context)
        target_crs = self.parameterAsCrs(parameters, self.TARGET_CRS, context)
        apply_div_b = self.parameterAsBoolean(parameters, self.APPLY_DIVISOR_B, context)
        divisor_b = self.parameterAsDouble(parameters, self.DIVISOR_B, context)

        out_a_class = self.parameterAsOutputLayer(parameters, self.OUT_A_CLASS, context)
        out_b_class = self.parameterAsOutputLayer(parameters, self.OUT_B_CLASS, context)
        out_bivar = self.parameterAsOutputLayer(parameters, self.OUT_BIVAR, context)
        out_qml = self.parameterAsFileOutput(parameters, self.OUT_QML, context)

        tmpdir = tempfile.mkdtemp(prefix='bivar_')

        # ---------- Reproject & Align ----------
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
                'RESAMPLING': 1,  # Bilinear
                'DATA_TYPE': 5,   # Float32
                'TARGET_EXTENT': te,
                'TARGET_EXTENT_CRS': t_srs.authid() if t_srs else ref_ds.GetProjection(),
                'X_RESOLUTION': px, 'Y_RESOLUTION': py,
                'MULTITHREADING': True,
                'OUTPUT': dst
            }
            for alg in ('gdal:warpreproject', 'gdal:warp'):
                try:
                    return processing.run(alg, args, context=context, feedback=feedback)
                except Exception:
                    continue
            raise RuntimeError("GDAL warp not available on this QGIS.")

        path_a, path_b = raster_a.source(), raster_b.source()

        if do_align:
            # Reproject A to target CRS if given; otherwise copy as GTiff to be reference
            a_ref = os.path.join(tmpdir, 'A_ref.tif')
            if target_crs.isValid():
                warp_to_match(path_a, a_ref, path_a, target_crs)
            else:
                gdal.Translate(a_ref, path_a, format='GTiff')

            # Ensure A grid is clean Float32 and standardized
            a_al = os.path.join(tmpdir, 'A_aligned.tif')
            warp_to_match(a_ref, a_al, a_ref, target_crs if target_crs.isValid() else None)

            # Align B to A grid/CRS
            b_al = os.path.join(tmpdir, 'B_aligned.tif')
            warp_to_match(path_b, b_al, a_al, target_crs if target_crs.isValid() else None)
        else:
            a_al = os.path.join(tmpdir, 'A_aligned.tif')
            b_al = os.path.join(tmpdir, 'B_aligned.tif')
            gdal.Translate(a_al, path_a, format='GTiff', outputType=gdal.GDT_Float32)
            gdal.Translate(b_al, path_b, format='GTiff', outputType=gdal.GDT_Float32)

        # ---------- Optional divide Raster B ----------
        b_input = b_al
        if apply_div_b:
            b_scaled = os.path.join(tmpdir, 'B_scaled.tif')
            qgis_expr = f' "B@1" / {divisor_b} '
            gdal_expr = f' B / {divisor_b} '
            _runcalc_dual(qgis_expr, gdal_expr, [b_al], b_scaled, feedback)
            b_input = b_scaled

        # ---------- Compute quantiles (terciles) ----------
        def quantiles(path):
            ds = gdal.Open(path)
            band = ds.GetRasterBand(1)
            arr = band.ReadAsArray().astype('float64')
            nd = band.GetNoDataValue()
            if nd is not None:
                arr = np.where(arr == nd, np.nan, arr)
            vals = arr[~np.isnan(arr)]
            if vals.size == 0:
                raise RuntimeError("No valid pixels for quantiles.")
            q1 = float(np.percentile(vals, 33.333))
            q2 = float(np.percentile(vals, 66.667))
            return q1, q2

        a_q1, a_q2 = quantiles(a_al)
        b_q1, b_q2 = quantiles(b_input)

        # ---------- Reclassify to 1/2/3 ----------
        qgis_expr_A = f'( "A@1" <= {a_q1} ) * 1 + ( ( "A@1" > {a_q1} ) AND ( "A@1" <= {a_q2} ) ) * 2 + ( "A@1" > {a_q2} ) * 3'
        gdal_expr_A = f'(A <= {a_q1}) * 1 + ((A > {a_q1}) * (A <= {a_q2})) * 2 + (A > {a_q2}) * 3'
        _runcalc_dual(qgis_expr_A, gdal_expr_A, [a_al], out_a_class, feedback)

        qgis_expr_B = f'( "B@1" <= {b_q1} ) * 1 + ( ( "B@1" > {b_q1} ) AND ( "B@1" <= {b_q2} ) ) * 2 + ( "B@1" > {b_q2} ) * 3'
        gdal_expr_B = f'(B <= {b_q1}) * 1 + ((B > {b_q1}) * (B <= {b_q2})) * 2 + (B > {b_q2}) * 3'
        _runcalc_dual(qgis_expr_B, gdal_expr_B, [b_input], out_b_class, feedback)

        # ---------- Combine into 11..33 ----------
        qgis_expr_AB = '( "A@1" * 10 ) + "B@1"'
        gdal_expr_AB = '(A * 10) + B'
        _runcalc_dual(qgis_expr_AB, gdal_expr_AB, [out_a_class, out_b_class], out_bivar, feedback)

        # ---------- QML write & apply ----------
        style_written = None
        if out_qml:
            style_written = write_bivariate_qml(out_qml)
            # Try to apply immediately (if algorithm exists)
            try:
                processing.run('qgis:applylayerstyle', {'INPUT': out_bivar, 'STYLE': style_written})
            except Exception:
                # Not all builds ship this alg; user can load style manually.
                pass

        feedback.pushInfo(f'Terciles A: q1={a_q1:.4f}, q2={a_q2:.4f}')
        feedback.pushInfo(f'Terciles B: q1={b_q1:.4f}, q2={b_q2:.4f}')

        results = {
            self.OUT_A_CLASS: out_a_class,
            self.OUT_B_CLASS: out_b_class,
            self.OUT_BIVAR: out_bivar
        }
        if style_written:
            results[self.OUT_QML] = style_written
        return results


def classFactory(iface=None):
    return BivariateClimateGenerator()
