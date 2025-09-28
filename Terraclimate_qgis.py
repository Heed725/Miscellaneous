## TerraClimate: Clip Remote NetCDF (xarray) to Layer (QGIS/GDAL clip) – CF attrs fix
## Requires: xarray, rioxarray, numpy

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing, QgsProcessingAlgorithm, QgsProcessingParameterVectorLayer,
    QgsProcessingParameterEnum, QgsProcessingParameterNumber, QgsProcessingParameterFileDestination,
    QgsProcessingException, QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsProject, QgsRasterLayer, QgsGeometry, QgsVectorLayer
)
import json, time, os, tempfile

class TerraClimateClipByYear_GDAL(QgsProcessingAlgorithm):
    INPUT_VECTOR='INPUT_VECTOR'; VARIABLE='VARIABLE'; YEAR='YEAR'; TIME_INDEX='TIME_INDEX'
    BUFFER_DEG='BUFFER_DEG'; MAX_RETRIES='MAX_RETRIES'; OUTPUT_TIF='OUTPUT_TIF'
    VAR_OPTIONS=['aet','def','pdsi','pet','ppt','q','soil','srad','swe','tmax','tmin','vap','vpd','ws']
    BASE_URL='http://thredds.northwestknowledge.net:8080/thredds/dodsC/TERRACLIMATE_ALL/data'

    def tr(self,t): return QCoreApplication.translate('TerraClimateClipByYear_GDAL', t)
    def createInstance(self): return TerraClimateClipByYear_GDAL()
    def name(self): return 'terraclimate_clip_remote_to_layer_gdalclip'
    def displayName(self): return self.tr('TerraClimate: Clip Remote NetCDF to Layer (QGIS/GDAL clip)')
    def group(self): return self.tr('Climate')
    def groupId(self): return 'climate'
    def shortHelpString(self): return self.tr('Remote subset with xarray, then GDAL mask clip. Choose variable & year (1958–2024).')

    def initAlgorithm(self, config=None):
        from qgis.core import QgsProcessingParameterEnum, QgsProcessingParameterNumber, QgsProcessingParameterFileDestination
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_VECTOR,'Input polygon layer',[QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterEnum(self.VARIABLE,'TerraClimate variable',options=self.VAR_OPTIONS,defaultValue=self.VAR_OPTIONS.index('tmax')))
        self.addParameter(QgsProcessingParameterNumber(self.YEAR,'Year (1958–2024)',type=QgsProcessingParameterNumber.Integer,defaultValue=2022,minValue=1958,maxValue=2024))
        self.addParameter(QgsProcessingParameterNumber(self.TIME_INDEX,'TIME_INDEX (-1 = all months; else 1–12)',type=QgsProcessingParameterNumber.Integer,defaultValue=-1,minValue=-1,maxValue=366))
        self.addParameter(QgsProcessingParameterNumber(self.BUFFER_DEG,'Bounding-box buffer (degrees)',type=QgsProcessingParameterNumber.Double,defaultValue=0.1))
        self.addParameter(QgsProcessingParameterNumber(self.MAX_RETRIES,'Max retries (dataset open)',type=QgsProcessingParameterNumber.Integer,defaultValue=3,minValue=1,maxValue=10))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_TIF,'Output clipped GeoTIFF','GeoTIFF (*.tif *.tiff)'))

    def _ensure_layer(self, maybe_layer, name_hint='mask'):
        if hasattr(maybe_layer,'getFeatures'): return maybe_layer
        if isinstance(maybe_layer,str):
            lyr=QgsVectorLayer(maybe_layer,name_hint,'ogr')
            return lyr if lyr and lyr.isValid() else None
        return None

    def processAlgorithm(self, parameters, context, feedback):
        # deps
        try:
            import xarray as xr, rioxarray, numpy as np, processing
        except Exception as e:
            raise QgsProcessingException(f'Missing packages: {e}')

        # inputs
        layer=self.parameterAsVectorLayer(parameters,self.INPUT_VECTOR,context)
        if layer is None: raise QgsProcessingException('Invalid input vector layer.')
        var_name=self.VAR_OPTIONS[self.parameterAsEnum(parameters,self.VARIABLE,context)]
        year=self.parameterAsInt(parameters,self.YEAR,context)
        time_index=self.parameterAsInt(parameters,self.TIME_INDEX,context)
        buffer_deg=float(self.parameterAsDouble(parameters,self.BUFFER_DEG,context))
        max_retries=self.parameterAsInt(parameters,self.MAX_RETRIES,context)
        out_tif=self.parameterAsFileOutput(parameters,self.OUTPUT_TIF,context)
        if not (1958<=year<=2024): raise QgsProcessingException('Year must be in 1958–2024.')

        url=f'{self.BASE_URL}/TerraClimate_{var_name}_{year}.nc'
        feedback.pushInfo(f'Using dataset: {url}')

        # transforms & extent (from input layer)
        crs_src=layer.crs(); crs_wgs=QgsCoordinateReferenceSystem('EPSG:4326')
        if not crs_src.isValid(): raise QgsProcessingException('Input layer has invalid CRS.')
        xform=QgsCoordinateTransform(crs_src,crs_wgs,QgsProject.instance()) if crs_src!=crs_wgs else None

        extent_wgs=None
        for f in layer.getFeatures():
            g=f.geometry()
            if not g or g.isEmpty(): continue
            g_wgs=QgsGeometry.fromWkt(g.asWkt())
            if xform and g_wgs.transform(xform)!=0: raise QgsProcessingException('Failed to reproject geometry to EPSG:4326.')
            try: g_wgs=g_wgs.buffer(0,1)
            except Exception: pass
            extent_wgs=g_wgs.boundingBox() if extent_wgs is None else extent_wgs.combineExtentWith(g_wgs.boundingBox())
        if extent_wgs is None: raise QgsProcessingException('No valid geometries found.')

        minx=extent_wgs.xMinimum()-buffer_deg; miny=extent_wgs.yMinimum()-buffer_deg
        maxx=extent_wgs.xMaximum()+buffer_deg; maxy=extent_wgs.yMaximum()+buffer_deg

        # dissolve for clean cutline
        try:
            dis=processing.run("native:dissolve",
                {"INPUT":layer,"FIELD":[],"SEPARATE_DISJOINT":False,"OUTPUT":QgsProcessing.TEMPORARY_OUTPUT},
                context=context,is_child_algorithm=True)
            mask_layer=self._ensure_layer(dis["OUTPUT"],"mask_dissolved")
            if mask_layer is None:
                feedback.reportError('Dissolve returned a path that could not be loaded. Falling back to original layer.')
                mask_layer=layer
        except Exception as e:
            feedback.reportError(f'Warning: dissolve failed ({e}). Using original layer as mask.')
            mask_layer=layer

        # open dataset with retry
        ds,last_err=None,None
        for attempt in range(1,max_retries+1):
            if feedback.isCanceled(): break
            try:
                feedback.pushInfo(f'Opening remote dataset (Attempt {attempt}/{max_retries})…')
                ds=xr.open_dataset(url)
                feedback.pushInfo('Dataset opened successfully.')
                break
            except Exception as e:
                last_err=e; feedback.pushInfo(f'Failed to open dataset: {e}')
                if attempt<max_retries: time.sleep(5)
        if ds is None: raise QgsProcessingException(f'Could not open dataset after {max_retries} attempts. Last error: {last_err}')

        temp_unclipped=None
        try:
            if var_name not in ds.variables: raise QgsProcessingException(f'Variable "{var_name}" not in dataset.')
            da=ds[var_name]
            lon_name='lon' if 'lon' in da.dims else ('longitude' if 'longitude' in da.dims else None)
            lat_name='lat' if 'lat' in da.dims else ('latitude' if 'latitude' in da.dims else None)
            if lon_name is None or lat_name is None:
                raise QgsProcessingException(f'Could not find lon/lat dimensions. Dims: {da.dims}')

            # time
            if 'time' in da.dims and time_index!=-1:
                idx0=time_index-1
                if idx0<0 or idx0>=da.sizes['time']: raise QgsProcessingException(f'TIME_INDEX {time_index} out of range.')
                da=da.isel(time=idx0)

            # ensure CRS & spatial dims
            try: da=da.rio.write_crs("EPSG:4326", inplace=False)
            except Exception: pass
            da=da.rio.set_spatial_dims(x_dim=lon_name, y_dim=lat_name, inplace=False)

            # subset
            feedback.pushInfo('Step 1 (Fast): Selecting bounding box from remote server…')
            lon_vals,lat_vals=da[lon_name].values,da[lat_name].values
            lon_inc,lat_inc=lon_vals[0]<lon_vals[-1],lat_vals[0]<lat_vals[-1]
            lon_slice=slice(minx,maxx) if lon_inc else slice(maxx,minx)
            lat_slice=slice(miny,maxy) if lat_inc else slice(maxy,miny)
            sub=da.sel({lon_name:lon_slice, lat_name:lat_slice})
            if not lon_inc: sub=sub.sortby(lon_name)
            if not lat_inc: sub=sub.sortby(lat_name)
            try: sub=sub.rio.write_crs("EPSG:4326", inplace=False)
            except Exception: pass
            sub=sub.rio.set_spatial_dims(x_dim=lon_name, y_dim=lat_name, inplace=False)
            mb=float(sub.nbytes)/1e6 if hasattr(sub,'nbytes') else 0.0
            feedback.pushInfo(f'Downloaded a small subset of size: {mb:.2f} MB')

            # --- SANITIZE CF ATTRS (fix _FillValue error) ---
            def _sanitize_cf(arr):
                arr=arr.copy()
                # remove conflicting attrs
                for k in ['_FillValue','missing_value','scale_factor','add_offset']:
                    if k in arr.attrs: arr.attrs.pop(k, None)
                # and from encoding
                if hasattr(arr,'encoding') and isinstance(arr.encoding,dict):
                    for k in ['_FillValue','missing_value','scale_factor','add_offset']:
                        arr.encoding.pop(k, None)
                return arr

            sub=_sanitize_cf(sub)
            # set nodata + stable dtype for GeoTIFF
            try: sub=sub.rio.write_nodata(np.float32(-9999.0), inplace=False)
            except Exception: pass
            if str(sub.dtype)!='float32':
                sub=sub.astype('float32')

            # write temp unclipped tif
            fd, temp_unclipped = tempfile.mkstemp(suffix=".tif"); os.close(fd)
            feedback.pushInfo(f'Writing temporary subset raster: {temp_unclipped}')
            sub.rio.to_raster(temp_unclipped)

            # Step 2: GDAL clip
            feedback.pushInfo('Step 2 (QGIS): Clipping subset with mask layer (gdal:cliprasterbymasklayer)…')
            params={
                'INPUT': temp_unclipped,
                'MASK': mask_layer,
                'SOURCE_CRS': None,
                'TARGET_CRS': None,
                'NODATA': -9999.0,
                'ALPHA_BAND': False,
                'CROP_TO_CUTLINE': True,
                'KEEP_RESOLUTION': True,
                'SET_RESOLUTION': False,
                'X_RESOLUTION': None,
                'Y_RESOLUTION': None,
                'MULTITHREADING': True,
                'OPTIONS': '',
                'DATA_TYPE': 0,
                'EXTRA': '',
                'OUTPUT': out_tif
            }
            processing.run('gdal:cliprasterbymasklayer', params, context=context, feedback=feedback, is_child_algorithm=True)
            feedback.pushInfo('Clipping complete.')

        finally:
            try: ds.close()
            except Exception: pass
            if temp_unclipped and os.path.exists(temp_unclipped):
                try: os.remove(temp_unclipped)
                except Exception: pass

        # add to map
        name = out_tif.split('/')[-1] if '/' in out_tif else out_tif.split('\\')[-1]
        rlayer = QgsRasterLayer(out_tif, name)
        if not rlayer.isValid():
            feedback.reportError('Warning: Output raster saved but failed to load in QGIS.')
        else:
            QgsProject.instance().addMapLayer(rlayer)
        return {self.OUTPUT_TIF: out_tif}

TerraClimateClipByYear_GDAL()
