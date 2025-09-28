import xarray as xr
import geopandas as gpd
import rioxarray
import time # We need the time library to wait between retries

# --- (Inputs are the same) ---
shapefile_path = "c:/users/user/documents/Tanzania_Boundary.shp"
terraclimate_url = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/TERRACLIMATE_ALL/data/TerraClimate_tmax_2022.nc"
output_raster_path = "c:/users/user/documents/Tanzania_tmax_2022.tif"

# --- (Load Shapefile is the same) ---
print(f"Loading shapefile: {shapefile_path}")
tanzania_gdf = gpd.read_file(shapefile_path)

# --- NEW: OPEN DATASET WITH RETRY LOGIC ---
MAX_RETRIES = 3
ds = None # Initialize ds to None

for attempt in range(MAX_RETRIES):
    try:
        print(f"Opening remote dataset (Attempt {attempt + 1}/{MAX_RETRIES})...")
        ds = xr.open_dataset(terraclimate_url)
        print("Dataset opened successfully.")
        break # If successful, exit the loop
    except Exception as e:
        print(f"Failed to open dataset: {e}")
        if attempt < MAX_RETRIES - 1:
            print("Waiting 5 seconds before retrying...")
            time.sleep(5) # Wait for 5 seconds
        else:
            print("Max retries reached. Exiting.")
            exit() # Exit the script if all retries fail

# --- (The rest of the script is the same as before) ---

tmax_data = ds['tmax']
tmax_data = tmax_data.rio.write_crs("EPSG:4326", inplace=True)

if tanzania_gdf.crs != tmax_data.rio.crs:
    tanzania_gdf = tanzania_gdf.to_crs(tmax_data.rio.crs)

print("\nStep 1 (Fast): Selecting a bounding box from the remote server.")
minx, miny, maxx, maxy = tanzania_gdf.total_bounds
buffer = 0.1
lon_slice = slice(minx - buffer, maxx + buffer)
lat_slice = slice(maxy + buffer, miny - buffer)
tmax_subset = tmax_data.sel(lon=lon_slice, lat=lat_slice)
print(f"Downloaded a small subset of size: {tmax_subset.nbytes / 1e6:.2f} MB")

print("\nStep 2 (Precise): Clipping the subset to the Tanzania boundary.")
tanzania_tmax = tmax_subset.rio.clip(tanzania_gdf.geometry, drop=True)
print("Clipping complete.")

print(f"\nSaving clipped raster to: {output_raster_path}")
tanzania_tmax.rio.to_raster(output_raster_path)
print("\nProcess finished successfully!")
ds.close()
