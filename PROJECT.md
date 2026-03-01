# California Citrus Mapping Project

**Created:** 2026-02-28  
**Last Updated:** 2026-02-28  
**Location:** `/Users/lp1/clawd/landiq/`

## Overview

Interactive web map of California citrus parcels with owner/mailing address data from county parcel records. Features include:
- **Top 150 owners** color-coded by owner (fill color)
- **Packer identification** with colored borders (Cuties, Halos, Kings River, etc.)
- Other parcels shaded by planting year (white=old, dark blue=new)
- Editable RV_Owner and Packer fields via local dashboard
- Owner statistics: total acreage, average planting year, post-2018 acres
- **Year planted filter slider** (1984-2024) to filter parcels by planting date
- **Layer toggles** to show/hide owner colors and packer borders
- **Interactive tooltip** showing owner info, packer, acreage, year, and mailing address

**Live Map:** https://g3offers-netizen.github.io/ca-citrus-map-9b5810/

---

## Recent Changes (2026-02-28)

### Packer Field & Color-Coded Borders
Added `Packer` field to identify which packing house handles the fruit:

| Packer | Color | Acres | Parcels |
|--------|-------|-------|---------|
| Halos | 🔵 Blue (#0066ff) | 23,995 | 654 |
| Cuties | 🔴 Red (#ff0000) | 21,054 | 777 |
| Peelz | 🟠 Orange (#f97316) | 10,696 | 521 |
| Sunkist | 🟢 Green (#00cc66) | 6,505 | 423 |
| Kings River | 🟡 Yellow (#ffcc00) | 5,014 | 344 |
| Sumo | 🩷 Pink (#ff66b2) | 3,919 | 278 |
| Bee Sweet | 🟣 Purple (#9933ff) | 2,283 | 163 |

**Sources:**
- Dashboard manual edits (`packer_edits.json`)
- Outside Growers KMZ spatial overlay → "Peelz"

### Outside Growers Integration
- **Source:** `/Users/lp1/Downloads/Outside Growers.kmz`
- **Records:** 166 grower locations (LineString geometries)
- **Method:** Buffered lines by 50m, spatial intersect with citrus parcels
- **Result:** 521+ parcels tagged as "Peelz" packer
- **Standalone map:** `outside_growers_map.html`

### Layer Toggle Controls
Added checkboxes in control panel:
- ☑️ **Owner colors (Top 150)** — Toggle fill colors for top owners
- ☑️ **Packer borders** — Toggle colored borders by packer

Legends automatically hide/show based on toggle state.

### Year Planted Filter Slider
Dual-slider filter in top-right corner:
- Filter parcels by year planted range (1984-2024)
- Shows live parcel count as you filter
- Reset button to show all parcels

### Enhanced Tooltip
Tooltip now displays:
- **RV_Owner** (standardized owner name, bold)
- **Original Owner** (if different, italic gray)
- **Packer** (with color-coded emoji 🍊)
- Parcel acres
- County
- Year planted
- **Owner Total** (all acres owned by this RV_Owner)
- **Avg Year** (average planting year for owner group)
- **Post-2018 acres** (new plantings for owner group)
- **Mailing address with city** (where available)

### Madera County Data Added
- Source: `/Users/lp1/Downloads/Gis-CitrusbyCounty_062024/maderaintersection/maderaintersection.shp`
- Joined via UniqueID field
- **240 of 262** Madera parcels now have owner info
- Includes: OWNER_NAME, MAIL_ADDR, MAIL_CITY

### Dashboard Enhancements
- Added **Packer** editable column
- Packer edits saved to `packer_edits.json`
- Removed decimals from acres display
- Stats show both RV_Owner and Packer edit counts

---

## Data Sources

### 1. LandIQ 2024 Crop Mapping (Citrus Layer)
- **Source:** California Department of Water Resources via LandIQ
- **URL:** https://www.landiq.com/land-use-mapping
- **Download:** https://data.cnra.ca.gov/dataset/6c3d65e3-35bb-49e1-a51e-49d5a2cf09a9
- **File:** `i15_crop_mapping_2024_provisional.zip` (167MB)
- **Filter:** `MAIN_CROP = 'C'` (pure citrus only, excludes C6=olives, etc.)
- **Records:** 31,462 citrus parcels
- **Total Acres:** 312,618
- **Key Fields:** `YR_PLANTED`, `ACRES`, `COUNTY`, `MAIN_CROP`

### 2. County Parcel Data (Owner/Address)

| County | Source | Records | Format |
|--------|--------|---------|--------|
| Fresno | SF Premium 06019 | 314,255 | GDB |
| Kern | ca_kern.gdb | 419,614 | GDB |
| Tulare | ca_tulare.gdb | 162,914 | GDB |
| Madera | maderaintersection.shp | 528 | SHP |

**File Locations:**
- Fresno: `/Users/lp1/Downloads/zip1eaa0d6ed201710474124/SF_Premium_06019_20240115/Fresno_Parcels.gdb`
- Kern: `/Users/lp1/Downloads/ca_kern.gdb`
- Tulare: `/Users/lp1/Downloads/ca_tulare.gdb`
- Madera: `/Users/lp1/Downloads/Gis-CitrusbyCounty_062024/maderaintersection/maderaintersection.shp`

### 3. Outside Growers KMZ
- **File:** `/Users/lp1/Downloads/Outside Growers.kmz`
- **Contents:** 166 grower location LineStrings
- **Fields:** Name (grower-variety), description
- **Usage:** Spatial overlay to identify Peelz packer parcels

---

## County Coverage Summary

| County | Parcels | With Owner | Coverage |
|--------|---------|------------|----------|
| Tulare | 13,318 | 13,300 | 99.9% |
| Kern | 2,419 | 2,418 | 100% |
| Fresno | 4,471 | 4,431 | 99.1% |
| Madera | 262 | 240 | 91.6% |
| Other | 10,992 | 0 | 0% |
| **Total** | **31,462** | **20,389** | **65%** |

**Note:** Mailing city currently only available for Madera county parcels.

---

## Output Files

### Shapefiles
| File | Description | Records |
|------|-------------|---------|
| `california_citrus_only_2024.shp` | LandIQ citrus (filtered) | 31,462 |
| `citrus_with_rv_owner.shp` | **Main file** - citrus with all owner/packer data | 31,462 |

### HTML Maps
| File | Description |
|------|-------------|
| `citrus_with_slider.html` | **Current** - Main map with all features |
| `index.html` | Copy for GitHub Pages |
| `outside_growers_map.html` | Outside Growers KMZ visualization |

### Data/Config Files
| File | Purpose |
|------|---------|
| `rv_owner_edits.json` | User edits to RV_Owner (33 entries) |
| `packer_edits.json` | User edits to Packer (25 entries) |
| `top150_rv_owners.csv` | Top 150 by RV_Owner with stats |
| `top200_citrus_owners.csv` | Dashboard source data (200 entries) |

### GitHub Pages
| Map | URL |
|-----|-----|
| Citrus (main) | https://g3offers-netizen.github.io/ca-citrus-map-9b5810/ |
| Almonds | https://g3offers-netizen.github.io/ca-almonds-map-991a74/ |
| Olives | https://g3offers-netizen.github.io/ca-olives-map-e07e0d/ |

---

## Top 150 Owners Dashboard

**To open the dashboard:**
```bash
cd /Users/lp1/clawd/landiq
source venv/bin/activate
python3 owner_dashboard_server.py
# Then open: http://localhost:8765
```

Or just ask Gigi: *"open the citrus owner dashboard"*

### Dashboard Features
- **Editable columns:** Rv_Owner, Packer
- **SAVE ALL** button persists edits to JSON files
- **Export CSV** with edits included
- **Clear All Edits** button
- Stats show total acres, parcels, and edit counts

### Edit Files
| File | Purpose | Current Entries |
|------|---------|-----------------|
| `rv_owner_edits.json` | Standardized owner names | 33 |
| `packer_edits.json` | Packer assignments | 25 |

---

## 🔄 How to Update After Dashboard Edits

When Lee says **"update the database"** or **"update everything"**:

### Quick Command
Ask Gigi: *"update the database with the dashboard values and refresh the map"*

### Manual Steps

**Step 1: Apply edits to shapefile**
```python
import geopandas as gpd
import json

gdf = gpd.read_file('citrus_with_rv_owner.shp')

# Load edits
with open('rv_owner_edits.json') as f:
    rv_edits = json.load(f)
with open('packer_edits.json') as f:
    packer_edits = json.load(f)

# Apply RV_Owner edits
for idx, row in gdf.iterrows():
    mail_std = row.get('MAIL_STD')
    if mail_std and mail_std in rv_edits:
        gdf.at[idx, 'RV_OWNER'] = rv_edits[mail_std]
    if mail_std and mail_std in packer_edits:
        gdf.at[idx, 'Packer'] = packer_edits[mail_std]

gdf.to_file('citrus_with_rv_owner.shp')
```

**Step 2: Recalculate stats & regenerate map**
```python
# Recalculate RV_TOTAL, RV_PARCELS, AVG_YEAR, ACRES_2018
# Regenerate citrus_with_slider.html
# Copy to index.html
```

**Step 3: Push to GitHub**
```bash
cp citrus_with_slider.html index.html
git add index.html && git commit -m "Updated from dashboard" && git push
```

---

## Packer Color Reference

For use in map styling:

```javascript
var packerColors = {
    'Cuties': '#ff0000',      // Red
    'Halos': '#0066ff',       // Blue
    'Kings River': '#ffcc00', // Yellow
    'Bee Sweet': '#9933ff',   // Purple
    'Peelz': '#f97316',       // Orange
    'Sunkist': '#00cc66',     // Green
    'Sumo': '#ff66b2'         // Pink
};
```

---

## Technical Notes

### Spatial Join Method
Use **centroid-within** instead of **intersects** to avoid false matches with linear features (canals, roads):

```python
citrus_centroids = citrus.copy()
citrus_centroids['geometry'] = citrus_centroids.geometry.centroid
result = gpd.sjoin(citrus_centroids, parcels, predicate='within')
```

### Outside Growers Overlay
KMZ contains LineStrings, not polygons. Buffer by 50m before intersection:

```python
growers['geometry'] = growers.geometry.buffer(50)
intersecting = gpd.sjoin(citrus, growers, predicate='intersects')
```

### Shapefile Column Limitations
Shapefiles truncate column names to 10 characters. Use GeoPackage for longer names.

### Large File Handling
GitHub has 100MB limit. For maps >50MB:
- Simplify geometries: `gdf['geometry'] = gdf['geometry'].simplify(0.0003)`
- Select fewer columns for display

### Python Environment
```bash
cd /Users/lp1/clawd/landiq
source venv/bin/activate
# Key packages: geopandas, folium, pyogrio, pandas
```

---

## LandIQ Crop Codes Reference

| Code | Crop |
|------|------|
| C | Citrus (generic) |
| C6 | Olives |
| D12 | Almonds |
| D13 | Walnuts |
| D14 | Pistachios |

Full legend: https://www.landiq.com/_files/ugd/1cc799_41f94b4f33114ab3a43b2b1a9d7da8ca.pdf

---

## Future Enhancements

1. **Add more counties:** Ventura, San Diego, Riverside parcel data
2. **Vector tiles:** Convert to PMTiles for faster loading
3. **Auto-update:** Re-run annually when new LandIQ data releases
4. **Additional crops:** Expand to pistachios, walnuts, avocados
5. **Owner research:** Link to corporate records, beneficial ownership
6. **Packer coverage analysis:** Calculate % of citrus acres by packer
7. **Historical comparison:** Track year-over-year changes in ownership
