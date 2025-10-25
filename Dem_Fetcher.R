# Load required libraries
library(elevatr)
library(sf)
library(raster)

# Load the shapefile for Tanzania from the given file path
tanzania_sf <- st_read("C:/users/user/documents/Tanzania_0.shp")

# Get the elevation raster clipped to the boundaries of the shapefile
elev <- elevatr::get_elev_raster(
  locations = tanzania_sf,  # shapefile with polygon for Tanzania
  z = 7,                    # Zoom level for resolution
  clip = "locations"        # Clip the raster to the location's extent
)

# Define the output file path for the .tif file
output_file <- "C:/users/user/documents/tanzania_elevation.tif"

# Export the elevation raster as a .tif file
writeRaster(elev, filename = output_file, format = "GTiff", overwrite = TRUE)

# Confirmation message
cat("Raster saved as:", output_file)
