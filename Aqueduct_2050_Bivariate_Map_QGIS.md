# Creating an Aqueduct 2050 Bivariate Map in QGIS

This guide explains how to create a **4 × 4 bivariate map of water demand and available blue water in Africa** using **WRI Aqueduct 4.0** data and the **Bivariate QGIS Plugin v0.0.7**.

## 1. Install the Bivariate QGIS Plugin

1. Open QGIS.
2. Go to **Plugins → Manage and Install Plugins**.
3. Select **Install from ZIP**.
4. Choose the plugin ZIP file, for example:

   ```text
   bivariate_plugin-0.0.7.zip
   ```

5. Click **Install Plugin**.
6. Confirm that the plugin is enabled.

The plugin tools should appear under:

```text
Processing Toolbox → Bivariate QGIS Plugin → Cartography
```

## 2. Download the Aqueduct Data

Download **WRI Aqueduct 4.0 Water Risk Data** from:

<https://www.wri.org/data/aqueduct-global-maps-40-data>

Extract the downloaded archive. The dataset normally includes a File Geodatabase named something similar to:

```text
aqueduct-4-0-water-risk-data.gdb
```

## 3. Load the Future Annual Layer

1. Open **Layer → Add Layer → Add Vector Layer**.
2. For **Source type**, choose **Directory**.
3. Set the directory type to **OpenFileGDB**.
4. Browse to the complete `.gdb` folder.
5. Click **Add**.
6. Select the **future_annual** layer.

Loading the complete `.gdb` folder is safer than opening an individual `.gdbtable` file.

## 4. Identify the Required Fields

For the **Business-as-Usual scenario at the 2050 milestone**, use:

| Variable | Original Aqueduct field | Shortened Shapefile field |
|---|---|---|
| Water demand | `bau50_ww_x_r` | `bau50_ww_x` |
| Available blue water | `bau50_ba_x_r` | `bau50_ba_x` |

The field names may be shortened when the data is exported to Shapefile because Shapefile field names are limited to ten characters.

Right-click the layer and select **Open Attribute Table** to confirm which field names your layer contains.

## 5. Clip the Data to Africa

Load an Africa boundary layer, then prepare it:

1. Run **Fix Geometries** on the Africa boundary.
2. Run **Dissolve** without selecting a dissolve field. This creates one Africa polygon.
3. Open **Vector → Geoprocessing Tools → Clip**.
4. Use:

   - **Input layer:** `future_annual`
   - **Overlay layer:** dissolved Africa boundary

5. Save the result as a GeoPackage layer, for example:

   ```text
   aqueduct_africa_bau2050
   ```

### Optional reprojection

For an Africa-focused equal-area map, reproject the clipped layer to:

```text
ESRI:102022 — Africa Albers Equal Area Conic
```

> **Note:** WGS 84 / World Equidistant Cylindrical is not an equal-area projection.

## 6. Remove Missing and Invalid Values

The bivariate plugin may place null values in the lowest class, so extract only records with valid values before classification.

### How to run Extract by Expression

1. Open **Processing → Toolbox**.
2. Search for **Extract by expression**.
3. Double-click **Extract by expression** under **Vector selection**.
4. For **Input layer**, select the clipped Africa Aqueduct polygon layer.
5. Beside **Expression**, click the **ε expression button**.
6. Paste the correct expression for your field names.

### Expression for the original Aqueduct fields

Use this if the layer contains `bau50_ww_x_r` and `bau50_ba_x_r`:

```qgis
"bau50_ww_x_r" IS NOT NULL
AND "bau50_ba_x_r" IS NOT NULL
AND "bau50_ww_x_r" >= 0
AND "bau50_ba_x_r" >= 0
```

### Expression for shortened Shapefile fields

Use this if the layer contains `bau50_ww_x` and `bau50_ba_x`:

```qgis
"bau50_ww_x" IS NOT NULL
AND "bau50_ba_x" IS NOT NULL
AND "bau50_ww_x" >= 0
AND "bau50_ba_x" >= 0
```

7. Click **OK**.
8. Under **Matching features**, select either:

   - **Create Temporary Layer** for testing; or
   - **Save to GeoPackage** for a permanent output.

9. Click **Run**.
10. Rename the new layer:

    ```text
    Aqueduct Africa Valid Values
    ```

Use this extracted polygon layer for the bivariate classification.

### Verify the result

1. Right-click **Aqueduct Africa Valid Values**.
2. Select **Open Attribute Table**.
3. Confirm that the demand and available-water fields contain no blank, null, or negative values.

Zero is a valid value and should remain included.

## 7. Important Note About CSV Files

A CSV table normally has no polygon geometry. The bivariate plugin requires a spatial polygon layer.

If you loaded only a CSV:

1. Load the original Aqueduct basin polygon layer.
2. Right-click the basin layer and select **Properties → Joins**.
3. Click **+ Add new join**.
4. Use `pfaf_id` as the matching field in both datasets.
5. Apply the join.
6. Export the joined polygon layer to a GeoPackage.
7. Run **Extract by Expression** on the exported polygon layer.

Do not run the bivariate map tool directly on a non-spatial CSV.

## 8. Create the 4 × 4 Bivariate Classes

Open:

```text
Processing Toolbox
→ Bivariate QGIS Plugin
→ Cartography
→ Bivariate Choropleth Classification (Vector)
```

Use the following settings:

| Setting | Value |
|---|---|
| Input layer | `Aqueduct Africa Valid Values` |
| Variable 1 — vertical/Y | Available blue water field: `bau50_ba_x_r` or `bau50_ba_x` |
| Variable 2 — horizontal/X | Water demand field: `bau50_ww_x_r` or `bau50_ww_x` |
| Classification method | Quantile / Equal Count |
| Grid size | 4 × 4 |
| Output | Save to GeoPackage |

The plugin creates fields similar to:

| Output field | Meaning |
|---|---|
| `Var1_Class` | Available-water class from 1 to 4 |
| `Var2_Class` | Demand class from A to D |
| `Bi_Class` | Combined class from `A1` to `D4` |

### Class interpretation

| Code | Interpretation |
|---|---|
| `A1` | Low demand and low available water |
| `D1` | High demand and low available water — strongest imbalance |
| `A4` | Low demand and high available water — more favourable |
| `D4` | High demand and high available water |

The horizontal demand class appears first in the code, followed by the vertical available-water class.

## 9. Custom 4 × 4 Bivariate Colour Palette

Use this custom palette when you want the bivariate diamond to begin with white at the left/bottom corner and blend toward orange, cyan, and blue-purple.

### Diamond corner colours

| Position | Low demand — left | High demand — right |
|---|---|---|
| High available water — top | `#e3732b` | `#5b7bac` |
| Low available water — bottom | `#ffffff` | `#04b5de` |

The four corners are therefore:

- **Left/bottom:** `#ffffff`
- **Right/bottom:** `#e3732b`
- **Left/top:** `#04b5de`
- **Right/top:** `#5b7bac`

### Visualized 4 × 4 grid

The grid below is displayed with **high available water at the top** and **low available water at the bottom**. Water demand increases from left to right.

<table>
  <thead>
    <tr>
      <th>Available water</th>
      <th>Low demand</th>
      <th></th>
      <th></th>
      <th>High demand</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>High</th>
      <td style="background:#04b5de;color:#000;padding:18px;text-align:center"><code>#04b5de</code></td>
      <td style="background:#21a1ce;color:#000;padding:18px;text-align:center"><code>#21a1ce</code></td>
      <td style="background:#3e8fbe;color:#fff;padding:18px;text-align:center"><code>#3e8fbe</code></td>
      <td style="background:#5b7bac;color:#fff;padding:18px;text-align:center"><code>#5b7bac</code></td>
    </tr>
    <tr>
      <th></th>
      <td style="background:#4fc7e0;color:#000;padding:18px;text-align:center"><code>#4fc7e0</code></td>
      <td style="background:#64acc2;color:#000;padding:18px;text-align:center"><code>#64acc2</code></td>
      <td style="background:#7592a2;color:#fff;padding:18px;text-align:center"><code>#7592a2</code></td>
      <td style="background:#887882;color:#fff;padding:18px;text-align:center"><code>#887882</code></td>
    </tr>
    <tr>
      <th></th>
      <td style="background:#9cd7e5;color:#000;padding:18px;text-align:center"><code>#9cd7e5</code></td>
      <td style="background:#a4b6b6;color:#000;padding:18px;text-align:center"><code>#a4b6b6</code></td>
      <td style="background:#ac9585;color:#000;padding:18px;text-align:center"><code>#ac9585</code></td>
      <td style="background:#b67557;color:#fff;padding:18px;text-align:center"><code>#b67557</code></td>
    </tr>
    <tr>
      <th>Low</th>
      <td style="background:#ffffff;color:#000;padding:18px;text-align:center;border:1px solid #bbb"><code>#ffffff</code></td>
      <td style="background:#e6c0a9;color:#000;padding:18px;text-align:center"><code>#e6c0a9</code></td>
      <td style="background:#e3996a;color:#000;padding:18px;text-align:center"><code>#e3996a</code></td>
      <td style="background:#e3732b;color:#000;padding:18px;text-align:center"><code>#e3732b</code></td>
    </tr>
  </tbody>
</table>

### Palette string for the plugin

Copy the following line exactly:

```text
#ffffff,#e6c0a9,#e3996a,#e3732b,#9cd7e5,#a4b6b6,#ac9585,#b67557,#4fc7e0,#64acc2,#7592a2,#887882,#04b5de,#21a1ce,#3e8fbe,#5b7bac
```

The sequence is organized from the bottom row to the top row. Within each row, the colours run from low demand on the left to high demand on the right.

## 10. Apply the 4 × 4 Colour Scheme

Open:

```text
Processing Toolbox
→ Bivariate QGIS Plugin
→ Cartography
→ Apply Bivariate Color Scheme (Vector)
```

Use:

| Setting | Value |
|---|---|
| Input layer | Output from the classification tool |
| Bivariate class field | `Bi_Class` |
| Colour palette | `BlueRed` |
| Grid size | 4 × 4 |
| Transpose axes | Off |
| Outline colour | Dark grey or the map background colour |
| Outline width | `0.05` or `0` |

Keep **Transpose axes** turned off because demand is already on the X-axis and available water is on the Y-axis.

### Suggested map styling

- Set the project background to `#11151A`.
- Use no basin outline or a very thin outline.
- Place national boundaries above the basin layer.
- Use a thin, partly transparent light-grey line for national boundaries.
- Keep the ocean and surrounding background dark.

## 11. Create the Diamond Legend

1. Open **Project → New Print Layout**.
2. Add the map using **Add Item → Add Map**.
3. Select **Add Item → Bivariate Diamond Legend**.
4. Draw the legend area on the layout.
5. Under **Item Properties**:

   - Select the styled bivariate output as the source layer.
   - Click **Rescan layout**.
   - Confirm that the grid size is **4 × 4**.
   - Turn off class codes for the final map if they are not needed.
   - Enable **Fit and centre**.
   - Reduce the gaps between cells.

Use these axis labels:

- **Horizontal/X axis:** Water demand
- **Vertical/Y axis:** Available blue water

If the diamond legend does not display its axis labels, add text labels and arrows manually in the Print Layout:

- Low demand
- High demand
- Low available water
- High available water

The regular **Bivariate Box Legend** can also be used if automatic X/Y labels are preferred.

## 12. Complete the Print Layout

### Suggested title

```text
Water Demand and Available Blue Water in Africa
Business-as-Usual Scenario, 2050
```

### Suggested methodological note

```text
Each variable is classified into Africa-wide quartiles. Colours show the
combination of relative water demand and available blue water, not absolute
water-stress thresholds.
```

### Suggested source text

```text
Source: WRI Aqueduct 4.0 — Future Annual, BAU 2050.
World Resources Institute; Kuzma et al. (2023).
```

Export through **Layout → Export as PNG** or **Export as PDF** at **300 DPI** or higher.

## 13. Water Stress Versus the Two-Variable Map

This bivariate map displays water demand and available blue water as two separate variables. It helps show combinations such as high demand with low available water.

If you want WRI's calculated water-stress indicator instead, use:

```text
bau50_ws_x_r
```

Water stress represents demand relative to available supply. Therefore, a map of `bau50_ws_x_r` is not the same as the bivariate demand-versus-available-water map described in this guide.

## Quick Workflow Summary

```text
Download Aqueduct 4.0
→ Load future_annual
→ Clip to Africa
→ Extract valid demand and available-water records
→ Run 4 × 4 quantile bivariate classification
→ Apply the bivariate colour scheme
→ Add the diamond legend
→ Complete the Print Layout
→ Export at 300 DPI
```
