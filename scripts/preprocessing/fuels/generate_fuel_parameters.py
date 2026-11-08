import sys
import json
import os
import shutil
import numpy as np
from osgeo import gdal
from collections import Counter
import rasterio
from rasterio.windows import from_bounds, Window
from rasterio.warp import transform_bounds
from rasterio.errors import WindowError
import pandas as pd

utils_path = f"{os.environ['PCB_SCRIPTS_DIR']}/utils"
out_path = os.environ["PCB_OUT_DIR"]
os.system(f"python {os.environ['PCB_OVERWRITE_PROFILE_VARS']}")

sys.path.append(utils_path)
from geoutils import bound_expansion

path = f"{out_path}"
fbp_json_path = f"{path}/profile/fbp.json"

with open(f'{path}/profile/config.json', 'r') as f:
    data = json.load(f)
    bounds = tuple(data["bounds"])
north, east, south, west = bound_expansion((bounds[0][1], bounds[0][0]), (bounds[1][1], bounds[1][0]))
print(f"North: {north}, East: {east}, South: {south}, West: {west}")

def compute_species_name(species_arr, key, region=None):
    if region == "Overall":
        region = None
    
    s = 0
    weight_s = 0
    for obj in species_arr:
        w = obj["weight"]
        weight_s += w
        if type(obj[key]) is dict:
            if region is not None and region in obj[key]:
                s += obj[key][region] * w
            elif "Overall" in obj[key]:
                s += obj[key]["Overall"] * w
            else:
                s += list(obj.values())[0] * w
        else:
            s += obj[key] * w
    return s / weight_s

regions = {}
with open(fbp_json_path, "r") as f:
    fbp = json.load(f)

# Get Unique regions
for id_str, obj in fbp.items():
    if "species" not in obj:
        continue
    for specie in obj["species"]:
        for key, val in specie.items():
            if key == "name" or key == "weight" or type(val) is not dict:
                continue
            if key not in regions:
                regions[key] = set()
            regions[key].update(val.keys())

# Get the region ofr each parameter
param_region_map = {}
for key, r in regions.items():
    r = list(r)
    r.sort()
    for i in range(len(r)):
        print(f"{i + 1}: {r[i]}")
    in_str = input(f"Enter a region selection for {key} (1 - {len(r)}):").strip()
    region_i = int(in_str) - 1
    param_region_map[key] = r[region_i] 
    print(f"Using region: {param_region_map[key]} for {key}")


crosswalks = []
for profile in os.scandir(f"{path}/output/crosswalk"):
    if not profile.is_dir():
        continue
    
    label = profile.name
    csvs = os.scandir(profile.path)
    for csv in csvs:
        if not csv.is_file() or not csv.name.endswith('.csv'):
            continue

        crosswalks.append((label, csv.name, csv.path))
crosswalks.sort()

for i in range(len(crosswalks)):
    print(f"{i + 1}: {crosswalks[i][0]}, {crosswalks[i][1]}")
in_str = input(f"Enter a crosswalk selection (1 - {len(crosswalks)}):").strip()
crosswalk_i = int(in_str) - 1
crosswalk_profile, crosswalk_name, crosswalk_path = crosswalks[crosswalk_i]
print(f"Using crosswalk: {crosswalk_profile}, {crosswalk_name}")

canada_file = out_path + '/data/FBP_fueltypes_Canada_30m/FBP_fueltypes_Canada_30m_EPSG3978_20240522.tif'

bbox_crs = "EPSG:4326"
counts = Counter()
with rasterio.open(canada_file) as src:
    # Transform bounds into the raster CRS (densify_pts handles projection curvature)
    left, bottom, right, top = transform_bounds(
        bbox_crs, src.crs, west, south, east, north, densify_pts=21
    )

    # Pixel window for the bbox, clipped to the raster extent
    bbox_win = from_bounds(left, bottom, right, top, transform=src.transform)
    bbox_win = bbox_win.round_offsets().round_lengths()
    bbox_win = bbox_win.intersection(Window(0, 0, src.width, src.height))

    for _, block_win in src.block_windows(1):
        try:
            win = block_win.intersection(bbox_win)   # only the part inside the bbox
        except WindowError:
            continue                                 # block is entirely outside

        block = src.read(1, window=win, masked=True).compressed()
        if block.size == 0:
            continue
        vals, cnts = np.unique(block, return_counts=True)
        counts.update(dict(zip(vals.tolist(), cnts.tolist())))

freq = (pd.Series(counts, name="count")
          .rename_axis("value").sort_index().reset_index())

cad_fuel_counts = dict(counts)

us_fuel_dict = {}
with open(crosswalk_path, "r") as crosswalk:
    crosswalk_data = crosswalk.readlines()[1:]
    for line in crosswalk_data:
        cad_id, _, us_id = line.strip().split(",")
        us_id = int(us_id.strip())
        cad_id = int(cad_id.strip())
        
        if str(cad_id) not in fbp:
            print(cad_id, "not in fbp")
            continue
        for key, val in fbp[str(cad_id)].items():
            if key == "name":
                continue
            if key == "species":
                for k, v in val[0].items():
                    if k == "name" or k == "weight":
                        continue
                    if k not in us_fuel_dict:
                        us_fuel_dict[k] = {}
                    if us_id not in us_fuel_dict[k]:
                        us_fuel_dict[k][us_id] = {}
                        us_fuel_dict[k][us_id]["weighted_vals"] = 0
                        us_fuel_dict[k][us_id]["weights"] = 0
                    us_fuel_dict[k][us_id]["weighted_vals"] += cad_fuel_counts.get(cad_id, 0) * compute_species_name(val, k, param_region_map[k])
                    us_fuel_dict[k][us_id]["weights"] += cad_fuel_counts.get(cad_id, 0)
            else: 
                if key not in us_fuel_dict:
                    us_fuel_dict[key] = {}
                if us_id not in us_fuel_dict[key]:
                    us_fuel_dict[key][us_id] = {}
                    us_fuel_dict[key][us_id]["weighted_vals"] = 0
                    us_fuel_dict[key][us_id]["weights"] = 0
                    
                us_fuel_dict[key][us_id]["weighted_vals"] += cad_fuel_counts.get(cad_id, 0) * val
                us_fuel_dict[key][us_id]["weights"] += cad_fuel_counts.get(cad_id, 0)

for key, types in us_fuel_dict.items():
    print(f"-- {key} -- ")
    sorted_types = list(types.keys())
    sorted_types.sort()
    for t in sorted_types:
        if types[t]["weights"] == 0:
            continue
        print(f"{t}: {types[t]['weighted_vals'] / types[t]['weights']}")