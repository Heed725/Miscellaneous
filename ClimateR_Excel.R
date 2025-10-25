# Load required libraries
library(climateR)
library(terra)
library(tidyterra)
library(ggplot2)
library(sf)
library(colorspace)
library(showtext)
library(dplyr)
library(writexl)  # for Excel output

# Load Barlow font (optional)
font_add(family = "Barlow", regular = "Barlow-Regular.ttf")
showtext_auto()

# Load shapefile
NORTH <- st_read("C:/Users/user/Desktop/Project_North_Outputs_2/North_Region.shp")

# Download TerraClimate precipitation data for 2021
test_data <- getTerraClim(
  AOI = NORTH,
  varname = "ppt",
  startDate = "2023-01-01",
  endDate   = "2023-12-01"
)

# Extract the ppt raster stack (12 monthly layers)
ppt_stack <- test_data[[1]]

# Mask and project to shapefile CRS
ppt_stack <- mask(project(ppt_stack, crs(NORTH)), vect(NORTH))

# Extract mean monthly precipitation
monthly_means <- global(ppt_stack, fun = "mean", na.rm = TRUE)

# Prepare final dataframe
month_names <- month.name  # Jan to Dec
precip_df <- data.frame(
  Year = 2023,
  Month = month_names,
  Mean_Precip_mm = round(as.numeric(monthly_means$mean), 2)
)

# Export to Excel
write_xlsx(precip_df, "C:/Users/user/Desktop/Monthly_Precipitation_2023.xlsx")
