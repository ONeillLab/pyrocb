

import json
import os
import sys
import numpy as np
from osgeo import gdal


path = f"{sys.argv[1]}"
with open(f'{path}/profile/config.json', 'r') as f:
    data = json.load(f)
    bounds = tuple(data["bounds"])

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

for i in range(len(crosswalks)):
    print(f"{i + 1}: {crosswalks[i][0]}, {crosswalks[i][1]}")
crosswalk_i = int(input(f"Enter a crosswalk selection (1 - {len(crosswalks)}):")) - 1
crosswalk_profile, crosswalk_name, crosswalk_path = crosswalks[i]
print(f"Using crosswalk: {crosswalk_profile}, {crosswalk_name}")

crosswalk = {}
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
        crosswalk[canadian_id] = us_id

input_file = f"{sys.path}/data/FBP_fueltypes_Canada_30m/FBP_fueltypes_Canada_30m/FBP_fueltypes_Canada_30m_EPSG3978_20240522.tif"
output_file = f"{sys.path}/data/FBP_fueltypes_Canada_30m/FBP_fueltypes_Canada_30m/walked_FBP_fueltypes_Canada_30m_EPSG3978_20240522.tif"
west, south, = bounds[0]
east, north = bounds[1]

clipped_file = f"{sys.path}/data/FBP_fueltypes_Canada_30m/FBP_fueltypes_Canada_30m/FBP_fueltypes_Canada_30m_EPSG3978_20240522_clipped.tif"
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
assert all(0 <= v <= 14 for v in unique_out), \
    f'OUTPUT OUT OF RANGE - values outside [0,14]: {[v for v in unique_out if not 0<=v<=14]}'
print('Output range valid for var_wisdom category_range [0,14]')

driver = gdal.GetDriverByName('GTiff')
out_ds = driver.Create(output_file, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Int16)
out_ds.SetGeoTransform(gt)
out_ds.SetProjection(proj)
out_ds.GetRasterBand(1).WriteArray(output)
out_ds.GetRasterBand(1).SetNoDataValue(14)
out_ds = None
ds = None
