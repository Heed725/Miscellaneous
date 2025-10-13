# ---- Load package ----
if (!require(colorspace)) install.packages("colorspace")
library(colorspace)

# ---- Get all HCL palettes ----
pal_df <- colorspace::hcl_palettes(plot = FALSE)

# ---- Create empty output frame ----
palette_data <- data.frame(
  Palette = character(),
  Type = character(),
  HexCodes = character(),
  stringsAsFactors = FALSE
)

# ---- Loop through all palettes ----
for (i in seq_len(nrow(pal_df))) {
  pal_name <- rownames(pal_df)[i]
  pal_type <- pal_df$type[i]
  
  # Select function depending on palette type
  if (grepl("Qualitative", pal_type, ignore.case = TRUE)) {
    cols <- qualitative_hcl(9, palette = pal_name)
  } else if (grepl("Sequential", pal_type, ignore.case = TRUE)) {
    cols <- sequential_hcl(9, palette = pal_name)
  } else if (grepl("Diverging", pal_type, ignore.case = TRUE)) {
    cols <- diverging_hcl(9, palette = pal_name)
  } else {
    next
  }
  
  # Create a row for each palette with hex codes as a string
  hex_codes <- paste(cols, collapse = ", ")  # Joining hex codes into one string
  
  # Append to the main data frame
  temp <- data.frame(
    Palette = pal_name,
    Type = pal_type,
    HexCodes = hex_codes,
    stringsAsFactors = FALSE
  )
  
  palette_data <- rbind(palette_data, temp)
}

# ---- Save as CSV ----
write.csv(palette_data, "colorspace_palettes_hex_horizontal.csv", row.names = FALSE)

# ---- Done ----
cat("✅ Exported", nrow(palette_data), "rows from", length(unique(palette_data$Palette)), "palettes.\n")
