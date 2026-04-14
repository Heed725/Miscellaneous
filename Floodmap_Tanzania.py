"""
Flood Inventory Map — Tanzania
================================
Creates a 10 km × 10 km grid of unique flood event counts for Tanzania
using the Google Groundsource dataset (2000–2025).

Data sources
------------
- Google Groundsource: https://zenodo.org/records/18647054
- Natural Earth Admin0: https://naciscdn.org/naturalearth/10m/cultural/

Output
------
output/flood_inventory_grid_tanzania.gpkg
"""

import os

import geopandas as gpd
import matplotlib.colors as mcolors  # noqa: F401 (kept for optional custom styling)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Patch
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from shapely import STRtree
from shapely.geometry import box

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR   = "data"
OUTPUT_DIR = "output"
os.makedirs(DATA_DIR,   exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def download(url: str) -> str:
    """Download *url* into DATA_DIR if not already present; return local path."""
    from urllib.request import urlretrieve
    filename = os.path.join(DATA_DIR, os.path.basename(url).split("?")[0])
    if not os.path.exists(filename):
        local, _ = urlretrieve(url, filename)
        print(f"Downloaded {local}")
    return filename


# ---------------------------------------------------------------------------
# 1. Download inputs
# ---------------------------------------------------------------------------
SHAPEFILE   = "ne_10m_admin_0_countries_ind.zip"
PARQUET_FILE = "groundsource_2026.parquet"

download(f"https://naciscdn.org/naturalearth/10m/cultural/{SHAPEFILE}")
download(f"https://zenodo.org/records/18647054/files/{PARQUET_FILE}?download=1")

# ---------------------------------------------------------------------------
# 2. Load country boundary — Tanzania ISO 3166-1 alpha-3 = TZA
# ---------------------------------------------------------------------------
gdf_countries = gpd.read_file(os.path.join(DATA_DIR, SHAPEFILE), encoding="utf-8")
country = gdf_countries[gdf_countries["SOV_A3"] == "TZA"]

if country.empty:
    raise ValueError(
        "Tanzania not found. "
        "Check the shapefile column values with: gdf_countries['SOV_A3'].unique()"
    )

print(f"Country: {country['SOVEREIGNT'].values[0]}")

# ---------------------------------------------------------------------------
# 3. Build 10 km × 10 km grid
#    CRS: EPSG:21037  — UTM Zone 37S, suitable for mainland Tanzania.
#    Zanzibar/Pemba fall in Zone 38S; Zone 37S still gives good accuracy
#    for a country-wide inventory at 10 km resolution.
# ---------------------------------------------------------------------------
GRID_SIZE = 10_000   # metres
GRID_CRS  = "EPSG:21037"

country_proj = country.to_crs(GRID_CRS)
minx, miny, maxx, maxy = country_proj.total_bounds

xs = np.arange(minx, maxx, GRID_SIZE)
ys = np.arange(miny, maxy, GRID_SIZE)

polygons = [
    box(x, y, x + GRID_SIZE, y + GRID_SIZE)
    for x in xs
    for y in ys
]

grid = gpd.GeoDataFrame({"geometry": polygons}, crs=GRID_CRS)

# Keep only cells that intersect the country outline
grid_country = gpd.sjoin(
    grid, country_proj[["geometry"]],
    how="inner", predicate="intersects"
).drop(columns=["index_right"]).reset_index(drop=True)

print(f"Grid cells intersecting Tanzania: {len(grid_country):,}")

# ---------------------------------------------------------------------------
# 4. Load and spatially filter flood observations
# ---------------------------------------------------------------------------
gdf_all = gpd.read_parquet(os.path.join(DATA_DIR, PARQUET_FILE))

geometry_wgs84 = country.geometry.union_all()
xmin, ymin, xmax, ymax = geometry_wgs84.bounds
gdf_filtered = gdf_all.cx[xmin:xmax, ymin:ymax].copy()

print(f"Flood records within Tanzania bounding box: {len(gdf_filtered):,}")

# ---------------------------------------------------------------------------
# 5. Duplicate event detection
#    Spatially intersecting polygons with start_date within ±7 days are
#    treated as the same flood event and share a flood_event id.
# ---------------------------------------------------------------------------
gdf_flood = gdf_filtered.reset_index(drop=True)
dates = pd.to_datetime(gdf_flood["start_date"]).values
NDAYS = 7

tree = STRtree(gdf_flood.geometry.values)
left_idx, right_idx = tree.query(gdf_flood.geometry.values, predicate="intersects")

# Remove self-intersections and duplicate pairs
mask      = left_idx < right_idx
left_idx  = left_idx[mask]
right_idx = right_idx[mask]

date_diff_days = np.abs(
    (dates[left_idx] - dates[right_idx])
    .astype("timedelta64[D]")
    .astype(int)
)

time_mask   = date_diff_days <= NDAYS
nearby_left = left_idx[time_mask]
nearby_right = right_idx[time_mask]

n   = len(gdf_flood)
row = np.concatenate([nearby_left,  nearby_right])
col = np.concatenate([nearby_right, nearby_left])
graph = coo_matrix(
    (np.ones(len(row), dtype=np.int8), (row, col)),
    shape=(n, n)
)

n_components, labels = connected_components(graph, directed=False)
gdf_flood["flood_event"] = labels

print(f"Total polygons:          {n:>10,}")
print(f"Unique flood events:     {n_components:>10,}")
print(f"Avg polygons per event:  {n / n_components:>10.2f}")

# ---------------------------------------------------------------------------
# 6. Aggregate unique flood events to grid
# ---------------------------------------------------------------------------
gdf_reprojected = gdf_flood.to_crs(GRID_CRS)

joined = gpd.sjoin(
    grid_country, gdf_reprojected,
    how="inner", predicate="intersects"
)

counts = (
    joined.groupby(joined.index)["flood_event"]
    .nunique()
    .rename("flood_count")
)

grid_country["flood_count"] = (
    grid_country.index.map(counts).fillna(0).astype(int)
)

print(f"\nGrid cells with ≥1 flood event: "
      f"{(grid_country['flood_count'] > 0).sum():,} / {len(grid_country):,}")
print(f"Max flood events in a single cell: {grid_country['flood_count'].max()}")

# ---------------------------------------------------------------------------
# 7. Plot
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 10))

# Zero-count cells in neutral grey
grid_country[grid_country["flood_count"] == 0].plot(
    ax=ax, color="#d9d9d9", linewidth=0
)

# Non-zero cells coloured by flood count
CMAP = "YlOrRd"
VMAX = max(grid_country["flood_count"].quantile(0.99), 1)   # robust upper limit

non_zero = grid_country[grid_country["flood_count"] > 0]
non_zero.plot(
    ax=ax, column="flood_count",
    cmap=CMAP, vmin=1, vmax=VMAX, linewidth=0
)

# Colourbar
sm   = ScalarMappable(cmap=CMAP, norm=plt.Normalize(vmin=1, vmax=VMAX))
cbar = fig.colorbar(sm, ax=ax, shrink=0.5, pad=0.02)
cbar.set_label("Number of Unique Flood Events", fontsize=10)

# No-data legend entry
ax.legend(
    handles=[Patch(facecolor="#d9d9d9", label="No Observations")],
    loc="lower right", frameon=True
)

# Country outline
country_proj.plot(ax=ax, facecolor="none", edgecolor="#333333", linewidth=0.8)

ax.set_title("Tanzania — Flood Inventory (2000–2025)", fontsize=14, pad=12)
ax.axis("off")
plt.tight_layout()

map_path = os.path.join(OUTPUT_DIR, "flood_inventory_tanzania.png")
plt.savefig(map_path, dpi=150, bbox_inches="tight")
plt.show()
print(f"Map saved to {map_path}")

# ---------------------------------------------------------------------------
# 8. Save GeoPackage
# ---------------------------------------------------------------------------
out_path = os.path.join(OUTPUT_DIR, "flood_inventory_grid_tanzania.gpkg")
grid_country.to_file(out_path)
print(f"GeoPackage saved to {out_path}")
