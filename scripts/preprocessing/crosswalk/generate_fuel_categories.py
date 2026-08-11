
import json
import os
import sys
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

regions = set()
fbp = {}
with open(fbp_json_path, "r") as f:
    data = json.load(f)
    for id_str, obj in data.items():
        i = int(id_str)
        fbp[i] = {}
        
        for specie in obj["species"]:
            for key, val in specie.items():
                if key == "name" or key == "weight" or type(val) is not dict:
                    continue
                regions.update(val.keys())
    regions = list(regions)
    regions.sort()
    for i in range(len(regions)):
        print(f"{i + 1}: {regions[i]}")
    in_str = input(f"Enter a region selection (1 - {len(regions)}):").strip()
    region_i = int(in_str) - 1
    region = regions[region_i] 
    print(f"Using region: {region}")

    for id_str, obj in data.items():
        i = int(id_str)

        for key, val in obj.items():
            if key == "name":
                continue
            if key == "species":
                for k, v in val[0].items():
                    if k == "name" or k == "weight":
                        continue
                    fbp[i][k] = compute_species_name(val, k, region)
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

print(fbp)

crosswalk = {}
ids = list(fbp.keys())
ids.sort()
for i, can_id in enumerate(ids):
    crosswalk[can_id] = i + 1


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
for fbp, anderson in crosswalk.items():
    output[data == fbp] = anderson

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

os.system(f"""{sys.argv[1]}/.libraries/wrfxpy/convert_geotiff.sh {output_file} {path}/data/geog NFUEL_CAT""")
