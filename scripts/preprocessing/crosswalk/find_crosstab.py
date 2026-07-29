import sys
import numpy as np
import pandas as pd
import rasterio
import json
import os
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.warp import transform as warp_transform
from rasterio.windows import from_bounds, Window, bounds
from scipy.stats import chi2_contingency


def overlap_window(can, other):
    bounds = transform_bounds(other.crs, can.crs, *other.bounds)
    left = max(bounds[0], can.bounds.left)
    bottom = max(bounds[1], can.bounds.bottom)
    right = min(bounds[2], can.bounds.right)
    top = min(bounds[3], can.bounds.top)

    if left >= right or bottom >= top:
        return None

    win = from_bounds(left, bottom, right, top, transform=can.transform)
    return win.round_offsets().round_lengths()


def radius_window(canada, other, center_lon, center_lat, radius_km, radius_crs='EPSG:4326'):
    x, y = warp_transform(radius_crs, canada.crs, [center_lon], [center_lat])
    center_x, center_y = x[0], y[0]

    radius_m = radius_km * 1000

    left = center_x - radius_m
    right = center_x + radius_m
    bottom = center_y - radius_m
    top = center_y + radius_m

    # Start from the existing Canada/other overlap and clip it to the radius box
    base = overlap_window(canada, other)
    if base is None:
        return None

    base_bounds = bounds(base, canada.transform)

    left = max(left, base_bounds[0])
    bottom = max(bottom, base_bounds[1])
    right = min(right, base_bounds[2])
    top = min(top, base_bounds[3])

    if left >= right or bottom >= top:
        return None

    win = from_bounds(left, bottom, right, top, transform=canada.transform)
    return win.round_offsets().round_lengths()

def make_tiles(window, size):
    column_offset, row_offset = int(window.col_off), int(window.row_off)
    width, height = int(window.width), int(window.height)
    t = []
    for r in range(0, height, size):
        for c in range(0, width, size):
            t.append(Window(column_offset + c, row_offset + r, min(size, width - c), min(size, height - r)))
    return t


def crosstab_for_tile(canada, other, tile_window):

    canada_data = canada.read(1, window=tile_window)
    if not np.any(canada_data != NODATA):
        return None

    other_data = np.full(canada_data.shape, NODATA, dtype=canada_data.dtype)
    # Change data to be the same size
    reproject(
        source=rasterio.band(other, 1),
        destination=other_data,
        src_transform=other.transform, src_crs=other.crs,
        dst_transform=canada.window_transform(tile_window), dst_crs=canada.crs,
        resampling=Resampling.nearest,
    )

    mask = (canada_data != NODATA) & (other_data != NODATA) & (other_data != US_NODATA)
    if not np.any(mask):
        return None

    return pd.crosstab(canada_data[mask], other_data[mask])


def crosswalk(can_path, other_path, label, center_lon=None, center_lat=None, radius_km=None):
    with rasterio.open(can_path) as canada, rasterio.open(other_path) as other:
        if center_lon is not None and center_lat is not None and radius_km is not None:
            window = radius_window(canada, other, center_lon, center_lat, radius_km)
        else:
            window = overlap_window(canada, other)

        if window is None:
            print(f"No overlap between Canada and {label}")
            return pd.DataFrame()

        total = None
        tiles = make_tiles(window, TILE_SIZE)
        total_tiles = len(tiles)
        print(f"[{label}] Split overlapping region into {total_tiles} tiles.")
        for i in range(len(tiles)):
            print(f"[{label}] Tile: {i}/{total_tiles} ({i/total_tiles*100:.1f}%)")
            tile_window = tiles[i]
            result = crosstab_for_tile(canada, other, tile_window)
            if result is not None:
                total = result if total is None else total.add(result, fill_value=0)
        return total.fillna(0).astype(int) if total is not None else pd.DataFrame()
    
def save_crosswalk(total, label, out_dir='.'):
    if total is None or total.empty:
        print(f"[{label}] No data to save.")
        return

    path = f"{sys.argv[1]}/output/crosstab/{NAME}/crosswalk_{label}_counts.csv"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    total.to_csv(path)
    print(f"[{label}] Saved raw counts to {path}")

def significance_test(total, label):
    chi2, p, dof, expected = chi2_contingency(total.values)
    print(f"[{label}] chi2={chi2:.1f}, p={p:.2e}, dof={dof}")
    return chi2, p, expected
LONG = None
LAT = None
RADIUS_KM = None
NAME = ""
NODATA = -9999
US_NODATA = 32767
TILE_SIZE = 2 ** 13

canada_file = sys.argv[1] + '/data/FBP_fueltypes_Canada_30m/FBP_fueltypes_Canada_30m_EPSG3978_20240522.tif'
us_an_13_file = sys.argv[1] + '/data/LF2024_FBFM13_CONUS/LF2024_FBFM13_CONUS/Tif/LF2024_FBFM13_CONUS.tif'
ak_an_13_file = sys.argv[1] + '/data/LF2024_FBFM13_AK/LF2024_FBFM13_AK/Tif/LF2024_FBFM13_AK.tif'
us_sb_40_file = sys.argv[1] + '/data/LF2024_FBFM40_CONUS/LF2024_FBFM40_CONUS/Tif/LF2024_FBFM40_CONUS.tif'
ak_sb_40_file = sys.argv[1] + '/data/LF2024_FBFM40_AK/LF2024_FBFM40_AK/Tif/LF2024_FBFM40_AK.tif'

with open(f'{sys.argv[1]}/profile/config.json', 'r') as file:
    data = json.load(file)
    if data["crosswalk_radius"] is not None and data["crosswalk_radius"] != -1:
        RADIUS_KM = data["crosswalk_radius"]
        LONG, LAT = data["center"]
    NAME = data["name"]

print(f"{NAME} 13 Anderson Canada to Continental US Mapping")
us_an_13_crosstab = crosswalk(canada_file, us_an_13_file, f"{NAME}USAnderson13", center_lon=LONG, center_lat=LAT, radius_km=RADIUS_KM)
save_crosswalk(us_an_13_crosstab, f"{NAME}USAnderson13")
print(us_an_13_crosstab)

print(f"\n{NAME} 13 Anderson Canada to Alaska Mapping")
ak_an_13_crosstab = crosswalk(canada_file, ak_an_13_file, f"{NAME}AlaskaAnderson13", center_lon=LONG, center_lat=LAT, radius_km=RADIUS_KM)
save_crosswalk(ak_an_13_crosstab, f"{NAME}AlaskaAnderson13")
print(ak_an_13_crosstab)

print(f"\n{NAME} 13 Andersion Canada to Combined Mapping")
combined_an_13_crosstab = us_an_13_crosstab.add(ak_an_13_crosstab, fill_value=0).fillna(0).astype(int)
save_crosswalk(combined_an_13_crosstab, f"{NAME}CombinedAnderson13")
print(combined_an_13_crosstab)


print(f"\n{NAME} 40 Scott and Burgan to Continental US Mapping")
us_sb_40_crosstab = crosswalk(canada_file, us_sb_40_file, f"{NAME}USScottAndBurgan40", center_lon=LONG, center_lat=LAT, radius_km=RADIUS_KM)
save_crosswalk(us_sb_40_crosstab, f"{NAME}USScottAndBurgan40")
print(us_sb_40_crosstab)

print(f"\n{NAME} 40 Scott and Burgan Canada to Alaska Mapping")
ak_sb_40_crosstab = crosswalk(canada_file, ak_sb_40_file, f"{NAME}AlaskaScottAndBurgan40", center_lon=LONG, center_lat=LAT, radius_km=RADIUS_KM)
save_crosswalk(ak_sb_40_crosstab, f"{NAME}AlaskaScottAndBurgan40")
print(ak_sb_40_crosstab)

print(f"\n{NAME} 40 Scott and Burgan Canada to Combined Mapping")
combined_sb_40_crosstab = us_sb_40_crosstab.add(ak_sb_40_crosstab, fill_value=0).fillna(0).astype(int)
save_crosswalk(combined_sb_40_crosstab, f"{NAME}CombinedScottAndBurgan40")
