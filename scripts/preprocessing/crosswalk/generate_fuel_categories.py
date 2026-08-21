# Sylvio Dos Reis, 2026
# Attempts to create custom canadian fuel categories based on the fbp.json file
# It starts by filling in data from the fbp.json file. What cannot be determined from the fbp.json file is filled in via the selected crosswalk, and parameters deterimned from the usparams.csv
# It then crosswalks the Canadian categories to be consecutive digits, and prints namelist.fire varaibles sorted alphabetically.
# In order to run the geotiff, a custom var_wisdom script is used, located at override/wrfxpy/src/geo/var_wisdom.py. This copies the original var_wisdom script to out/temp/wrfxpy/src/geo/var_wisdom.py. In case of fail, it will attempt to copy the file back. It is worth checking to see if the original var_wisdom is properly located in out/wrfxpy/src/geo/var_wisdom.py in case of error, premature exit, or crash, otherwise the original var_wisdom file may be lost.
# Common errors include not having a "non fuel" category in fbp.json or the crosswalks, or not using consecutive digits for the US data types. See "a not ewhen using S&B 40 types"
# A note about "non fuel": make sure the "non fuel" category is the largest number in fbp.json. Commonly used is 9999
# A note when using the S&B 40 types: S&B 40 types need to be converted to consecutive 1-40 types before running this script (by modifying the crosswalk)

import json
import os
import sys
import shutil
import numpy as np
from osgeo import gdal
path = f"{sys.argv[1]}"
fbp_json_path = f"{path}/profile/fbp.json"
us_params_path = f"{path}/profile/us_params.csv"

with open(f'{path}/profile/config.json', 'r') as f:
    data = json.load(f)
    bounds = tuple(data["bounds"])

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
# Load anderson 13 data
# Generate a fbp -> anderson 13 crosswalk
# Generate new fgi and replacement values
# Generate namelist.fire
# Generate "walked" tiff (cropped)

regions = {}
fbp = {}
with open(fbp_json_path, "r") as f:
    data = json.load(f)

for id_str, obj in data.items():
    i = int(id_str)
    fbp[i] = {}
    if "species" not in obj:
        continue
    for specie in obj["species"]:
        for key, val in specie.items():
            if key == "name" or key == "weight" or type(val) is not dict:
                continue
            if key not in regions:
                regions[key] = set()
            regions[key].update(val.keys())

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

for id_str, obj in data.items():
    i = int(id_str)
    for key, val in obj.items():
        if key == "name":
            fbp[i]["fuel_name"] = val
        if key == "species":
            for k, v in val[0].items():
                if k == "name" or k == "weight":
                    continue
                fbp[i][k] = compute_species_name(val, k, param_region_map[k])
        else:
            fbp[i][key] = val
    
print(fbp)

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

with open(crosswalk_path, "r") as f:
    for line in f.read().strip().split("\n")[1::]:
        line = line.strip()
        if not line:
            continue
        canadian_id, canadian_name, us_id = line.split(",")
        canadian_id = int(canadian_id.strip())
        us_id = int(us_id.strip())

        if us_id == -9999:
            print(f"[WARN] Canadian ID {canadian_id} ({canadian_name.strip()}) is mapped to {us_id}")
        if canadian_id in fbp:
            fbp[canadian_id]["us_id"] = us_id

property_desc = {}
with open(us_params_path, "r") as f:
    for line in f.read().strip().split("\n")[1::]:
        line = line.strip()
        if not line:
            continue
        line = line.split(",")
        param_name = line[0]
        for key, val in fbp.items():
            if fbp[key]["us_id"] > len(fbp) - 1:
                i = 14
            else: 
                i = fbp[key]["us_id"]
            if param_name not in fbp[key]:
                fbp[key][param_name] = float(line[i].strip())
            else:
                print(f"Using Canadian values for {param_name}")
            property_desc[param_name] = line[-1].strip()

print(fbp)

crosswalk = {}
ids = list(fbp.keys())
ids.sort()
for i, can_id in enumerate(ids):
    crosswalk[can_id] = i + 1
print(crosswalk)
input_file = f"{path}/data/FBP_fueltypes_Canada_30m/FBP_fueltypes_Canada_30m_EPSG3978_20240522.tif"
output_file = f"{path}/data/FBP_fueltypes_Canada_30m/walked_FBP_fueltypes_Canada_30m_EPSG3978_20240522.tif"
west, south, = bounds[0]
east, north = bounds[1]

clipped_file = f"{path}/data/FBP_fueltypes_Canada_30m/FBP_fueltypes_Canada_30m_EPSG3978_20240522_clipped.tif"
if os.path.exists(clipped_file):
    os.remove(clipped_file)
gdal.Warp(clipped_file, input_file,
outputBounds = (west, south, east, north),
outputBoundsSRS = 'EPSG:4326',
srcSRS = 'EPSG:3978', dstSRS = "EPSG:4326",
resampleAlg = 'near', format = 'GTiff',
multithread = True
)

ds = gdal.Open(clipped_file)
band = ds.GetRasterBand(1)
data = band.ReadAsArray()
nodata = band.GetNoDataValue()
gt = ds.GetGeoTransform()
proj = ds.GetProjection()

print(f'Clipped array shape : {data.shape}')
print(f'Nodata value        : {nodata}')
print(f'Unique FBP values   : {np.unique(data)}')


output = np.full(data.shape, 14, dtype=np.int16) # Default type as no fuel, data types are 16 bit
for f, anderson in crosswalk.items():
    output[data == f] = anderson

unique_out = np.unique(output)
print(f'Unique output Anderson values: {unique_out}')

if os.path.exists(output_file):
    os.remove(output_file)
driver = gdal.GetDriverByName('GTiff')
out_ds = driver.Create(output_file, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Int16)
out_ds.SetGeoTransform(gt)
out_ds.SetProjection(proj)
out_ds.GetRasterBand(1).WriteArray(output)
out_ds.GetRasterBand(1).SetNoDataValue(14)
out_ds = None
ds = None

try:
    print("Saving old var_wisdom.py")
    os.makedirs(f'{sys.argv[1]}/temp/.libraries/wrfxpy/src/geo/', exist_ok=True)
    print("Overwritting var_wisdom.py")
    os.replace(f'{sys.argv[1]}/.libraries/wrfxpy/src/geo/var_wisdom.py', f'{sys.argv[1]}/temp/.libraries/wrfxpy/src/geo/var_wisdom.py')
    with open(f'{sys.argv[1]}/../override/wrfxpy/src/geo/var_wisdom.py') as f:
        varwisdom = f.read()
        print(f"{str(len(crosswalk))} FBP types found")
        varwisdom = varwisdom.replace("![NO_DATA]", str(len(crosswalk)))
    with open(f"{sys.argv[1]}/.libraries/wrfxpy/src/geo/var_wisdom.py", "w+") as f:
        f.write(varwisdom)

    print("Running convert_geotiff.sh")
    os.system(f"""{sys.argv[1]}/.libraries/wrfxpy/convert_geotiff.sh {output_file} {path}/data/geog NFUEL_CAT""")
    print("Removing overwritten var_wisdom.py")
    os.remove(f'{sys.argv[1]}/.libraries/wrfxpy/src/geo/var_wisdom.py')
except Exception as e:
    print("Error with custom fuel types")
    print(e)
finally:
    print("Returning original var_wisdom.py")
    shutil.copy(f'{sys.argv[1]}/temp/.libraries/wrfxpy/src/geo/var_wisdom.py', f'{sys.argv[1]}/.libraries/wrfxpy/src/geo/var_wisdom.py')

print("namelist.fire")
properties = set()
for i in ids:
    properties.update(list(fbp[i].keys()))
properties = list(properties)
properties.sort()
s = ""
for p in properties:
    l = ""
    if p in property_desc:
        l += f"!{property_desc[p]}\n"
    l += f"{p} = "
    for i in ids:
        if p in fbp[i]:
            if type(fbp[i][p]) is str:
                l += f"\"{fbp[i][p]}\", "
            else:
                l += f"{fbp[i][p]}, "
        else:
            l += "0, "
    l = l.strip()
    l = l.strip(",")
    s += f"{l}\n\n"
print(s)