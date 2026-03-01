# California Citrus Mapping Project

**Created:** 2026-02-28  
**Last Updated:** 2026-02-28  
**Location:** `/Users/lp1/clawd/landiq/`

## Overview

Interactive web map of California citrus parcels with owner/mailing address data from county parcel records. Features include:
- Top 150 owners color-coded by owner
- Other parcels shaded by planting year (white=old, dark blue=new)
- Editable RV_Owner field for standardizing owner names
- Owner statistics: total acreage, average planting year, post-2018 acres
- **Year planted filter slider** (1984-2024) to filter parcels by planting date
- **Interactive tooltip** showing owner info, acreage, year, and mailing address

## Recent Changes (2026-02-28)

### Year Planted Filter Slider
Added dual-slider filter in top-right corner:
- Filter parcels by year planted range (1984-2024)
- Shows live parcel count as you filter
- Reset button to show all parcels

### Enhanced Tooltip
Tooltip now displays:
- **RV_Owner** (standardized owner name)
- **Original Owner** (if different from RV_Owner)
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

### County Coverage Summary
| County | Parcels | With Owner | Coverage |
|--------|---------|------------|----------|
| Tulare | 13,318 | 13,300 | 99.9% |
| Kern | 2,419 | 2,418 | 100% |
| Fresno | 4,471 | 4,431 | 99.1% |
| Madera | 262 | 240 | 91.6% |
| Other | 10,992 | 0 | 0% |

**Note:** Mailing city currently only available for Madera county parcels.

**Live Map:** https://g3offers-netizen.github.io/ca-citrus-map-9b5810/

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

**Madera Fields Used:**
- `UNIQUEID` — Join key to LandIQ data
- `OWNER_NAME` — Property owner
- `MAIL_ADDR` — Mailing address
- `MAIL_CITY` — Mailing city

## Process

### Step 1: Filter LandIQ Data for Citrus
```python
import geopandas as gpd

gdf = gpd.read_file('i15_Crop_Mapping_2024_Provisional.shp')
citrus = gdf[gdf['MAIN_CROP'] == 'C'].copy()
citrus.to_file('california_citrus_only_2024.shp')
```

### Step 2: Spatial Join with County Parcels (Centroid Method)

**⚠️ IMPORTANT: Canal/Linear Parcel Fix**

Initial approach using `predicate='intersects'` caused false matches with linear parcels like the **Friant-Kern Canal**. These government-owned canal parcels (owned by "U S A WPRS") are long and thin, intersecting many citrus blocks they don't actually contain.

**Problem:** 130 citrus parcels falsely matched to "2800 COTTAGE WAY" (Bureau of Reclamation, Sacramento)

**Solution:** Use **centroid-within** instead of intersects:
1. Calculate centroid of each citrus parcel
2. Join where centroid falls WITHIN a county parcel
3. This ensures the citrus block is actually inside the parcel, not just touching it

**Result:** Canal false matches reduced from 130 to 3 parcels

```python
import geopandas as gpd

# Load citrus and reproject to California Albers (meters)
citrus = gpd.read_file('california_citrus_only_2024.shp')
citrus = citrus.to_crs(epsg=3310)

# Create centroids for citrus parcels
citrus_centroids = citrus.copy()
citrus_centroids['geometry'] = citrus_centroids.geometry.centroid

# Load parcels with key fields only
fresno = gpd.read_file('Fresno_Parcels.gdb', layer='ParcelsWithAssessments')
fresno = fresno.to_crs(epsg=3310)
fresno = fresno[['PARCEL_APN', 'OWNER_NAME', 'MAIL_ADDR', 'geometry']]
fresno.columns = ['FRESNO_APN', 'FRESNO_OWNER', 'FRESNO_MAIL', 'geometry']

# Spatial join using WITHIN (centroid must be inside parcel)
result = gpd.sjoin(citrus_centroids, fresno, how='left', predicate='within')
result = result.drop_duplicates(subset='UniqueID', keep='first')

# Repeat for Kern and Tulare...

# Restore original citrus geometries (not centroids) after join
result = result.drop(columns=['geometry'])
result = result.merge(citrus[['UniqueID', 'geometry']], on='UniqueID')
result = gpd.GeoDataFrame(result, geometry='geometry', crs='EPSG:3310')
result = result.to_crs(epsg=4326)

# Create unified fields
result['OWNER'] = result['FRESNO_OWNER'].fillna(result['KERN_OWNER']).fillna(result['TULARE_OWNER'])
result['MAIL'] = result['FRESNO_MAIL'].fillna(result['KERN_MAIL']).fillna(result['TULARE_MAIL'])
```

### Step 3: Address Standardization

Mailing addresses are standardized for consistent grouping:
- Uppercase all addresses
- `PO Box` / `P.O. BOX` → `PO BOX`
- `Avenue` / `Ave` / `Av` → `AVE`
- `Highway` / `Hwy` / `HW` → `HWY`
- `Street` / `Str` → `ST`
- `North/South/East/West` → `N/S/E/W`
- `Suite` / `#` → `STE`

**Result:** 3,590 unique addresses → 2,675 after standardization

### Step 4: RV_Owner Field (Revised Owner)

The `RV_OWNER` field allows manual standardization of owner names:
- Edits stored in `rv_owner_edits.json`
- If no edit exists, falls back to original `OWNER` value
- Dashboard at http://localhost:8765 for editing

Example edits:
```json
{
  "5001 CALIFORNIA AVE STE 230": "Wonderful",
  "33374 LERDO HWY": "Sun Pacific",
  "8570 S CEDAR AVE": "FPC",
  "12201 AVE 480": "Booth"
}
```

### Step 5: Calculate Owner Statistics

For each RV_Owner, calculate:
- `RV_TOTAL` - Total acres owned
- `RV_PARCELS` - Number of parcels
- `AVG_YEAR` - Average planting year
- `ACRES_2018` - Acres planted after 2018

```python
def calc_stats(group):
    return pd.Series({
        'AVG_YEAR': group['YR_PLANTED'].mean(),
        'ACRES_2018': group.loc[group['YR_PLANTED'] > 2018, 'ACRES'].sum()
    })

rv_stats = gdf.groupby('RV_OWNER').apply(calc_stats)
```

### Step 6: Create Interactive Map

**Map Styling:**
- **Top 100 owners:** Each assigned a unique color, white border
- **Other owners:** Shaded by planting year
  - White = Pre-1995 (oldest)
  - Light blue → Dark blue gradient
  - Dark blue = 2020+ (newest)

**Tooltip shows:**
- Owner / RV_Owner
- This parcel acres
- County
- Year planted
- Owner total acres
- Average planting year
- Post-2018 acres

## Output Files

### Current Shapefiles
| File | Description | Records |
|------|-------------|---------|
| `california_citrus_only_2024.shp` | LandIQ citrus (filtered) | 31,462 |
| `citrus_with_rv_owner.shp` | **Main file** - citrus with all owner data | 31,462 |
| `citrus_with_owners_fixed.shp` | After canal fix | 31,462 |

### HTML Maps
| File | Description |
|------|-------------|
| `citrus_top100_years.html` | **Current** - Top 100 colored + year shading |
| `tulare_parcels_map.html` | All Tulare county parcels |

### Data Files
| File | Purpose |
|------|---------|
| `rv_owner_edits.json` | User edits to RV_Owner (DO NOT DELETE) |
| `top100_rv_owners.csv` | Top 100 owners by acreage |
| `top100_citrus_owners.csv` | Dashboard source data |

### GitHub Pages
| Map | URL |
|-----|-----|
| Citrus (main) | https://g3offers-netizen.github.io/ca-citrus-map-9b5810/ |
| Almonds | https://g3offers-netizen.github.io/ca-almonds-map-991a74/ |
| Olives | https://g3offers-netizen.github.io/ca-olives-map-e07e0d/ |

## Results

### Citrus Parcels by County (with owner data)
| County | Citrus Parcels | With Owner Info | Coverage |
|--------|---------------|-----------------|----------|
| Tulare | 13,318 | 13,300 | 99.9% |
| Fresno | 4,471 | 4,431 | 99.1% |
| Kern | 2,419 | 2,418 | 100% |
| Madera | 262 | 240 | 91.6% |
| Other | 10,992 | 0 | 0% |
| **Total** | **31,462** | **20,389 (65%)** |

### Top 10 Owners (with RV_Owner edits)
| Rank | RV_Owner | Total Acres | Post-2018 Acres |
|------|----------|-------------|-----------------|
| 1 | Wonderful | 21,086 | 3,102 |
| 2 | Sun Pacific | 17,533 | 1,903 |
| 3 | FPC | 9,284 | 854 |
| 4 | Booth | 6,125 | — |
| 5 | Suntreat | 3,919 | 415 |
| 6 | Bronson Van Wyck | 3,643 | — |
| 7 | Gless | 3,609 | — |
| 8 | Sequoia Orange Company | 3,408 | — |
| 9 | Kings River | 2,960 | 536 |
| 10 | Yurosek | 2,885 | 1,608 |

## Top 150 Owners Dashboard (Editable)

**To open the dashboard:**
```bash
cd /Users/lp1/clawd/landiq
source venv/bin/activate
python3 owner_dashboard_server.py
# Then open: http://localhost:8765
```

Or just ask Gigi: *"open the citrus owner dashboard"*

**Files:**
| File | Purpose |
|------|---------|
| `owner_dashboard_server.py` | Local web server for editable dashboard |
| `rv_owner_edits.json` | Stores Rv_Owner edits (persists across sessions) |
| `top150_citrus_owners.csv` | Source data for dashboard |
| `top150_rv_owners.csv` | Top 150 by RV_Owner with stats |

**Features:**
- Editable `Rv_Owner` column for standardizing owner names
- Click **SAVE ALL** to persist edits to `rv_owner_edits.json`
- Export CSV with edits included
- Clear All Edits button

---

## 🔄 How to Update the Database After Dashboard Edits

When Lee says **"update the database"** after editing RV_Owner values in the dashboard:

### Step 1: Read the edits file
```python
with open('rv_owner_edits.json', 'r') as f:
    rv_edits = json.load(f)
```

### Step 2: Load the shapefile and apply RV_Owner
```python
gdf = gpd.read_file('citrus_with_totals_fixed.shp')

def get_rv_owner(row):
    mail = row.get('MAIL_STD')
    if mail and mail in rv_edits:
        return rv_edits[mail]
    return row.get('OWNER')  # Fall back to original owner

gdf['RV_OWNER'] = gdf.apply(get_rv_owner, axis=1)
```

### Step 3: Recalculate owner statistics for ALL owners
```python
def calc_stats(group):
    return pd.Series({
        'RV_TOTAL': group['ACRES'].sum(),
        'RV_PARCELS': len(group),
        'AVG_YEAR': group['YR_PLANTED'].mean(),
        'ACRES_2018': group.loc[group['YR_PLANTED'] > 2018, 'ACRES'].sum()
    })

rv_stats = gdf[gdf['RV_OWNER'].notna()].groupby('RV_OWNER').apply(calc_stats)
gdf = gdf.merge(rv_stats, on='RV_OWNER', how='left')
```

### Step 4: Save updated shapefile
```python
gdf.to_file('citrus_with_rv_owner.shp')
```

### Step 5: Generate top 150 CSV
```python
top150 = rv_stats.sort_values('RV_TOTAL', ascending=False).head(150)
top150.to_csv('top150_rv_owners.csv', index=False)
```

### Step 6: Recreate the map with top 150 colored
- Top 150 RV_Owners get unique colors
- Other owners shaded by planting year (white=old, dark blue=new)
- All parcels show owner totals in tooltip

### Step 7: Push to GitHub
```bash
cp citrus_top150_map.html index.html
git add index.html && git commit -m "Updated RV_Owner edits" && git push
```

**Key files that get updated:**
- `citrus_with_rv_owner.shp` — Main shapefile with RV_OWNER field
- `top150_rv_owners.csv` — Top 150 owners list
- `citrus_top150_map.html` — Interactive map
- `index.html` — GitHub Pages (copy of map)

**Files to NEVER overwrite:**
- `rv_owner_edits.json` — Lee's manual edits (only dashboard writes to this)

## LandIQ Crop Codes Reference

| Code | Crop |
|------|------|
| C | Citrus (generic) |
| C6 | Olives |
| D12 | Almonds |
| D13 | Walnuts |
| D14 | Pistachios |

Full legend: https://www.landiq.com/_files/ugd/1cc799_41f94b4f33114ab3a43b2b1a9d7da8ca.pdf

## Technical Notes

### Canal/Linear Feature Fix
Government-owned linear features (canals, roads, easements) can cause false spatial join matches. Always use **centroid-within** instead of **intersects** for parcel matching.

### Shapefile Column Limitations
Shapefiles truncate column names to 10 characters. When joining many columns, names can collide. **Solution:** Select only essential fields before joining, or use GeoPackage format instead.

### Large File Handling
GitHub has a 100MB file limit. For maps >50MB:
- Simplify geometries: `gdf['geometry'] = gdf['geometry'].simplify(0.0003)`
- Select fewer columns for display
- Consider vector tiles (PMTiles) for very large datasets

### Python Environment
```bash
cd /Users/lp1/clawd/landiq
source venv/bin/activate
# Key packages: geopandas, folium, pyogrio, pandas
```

## Future Enhancements

1. **Add more counties:** Ventura, San Diego, Riverside parcel data
2. **Vector tiles:** Convert to PMTiles for faster loading
3. **Auto-update:** Re-run annually when new LandIQ data releases
4. **Additional crops:** Expand to pistachios, walnuts, avocados
5. **Owner research:** Link to corporate records, beneficial ownership
