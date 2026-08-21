# Sylvio Dos Reis, 2026
# Downloads the high resolution elevation data
import json
import os
import sys
import requests
from osgeo import gdal
import numpy as np

bounds = ()
tiles = [] # Tiles needed for 
time = {}

with open(f'{sys.argv[1]}/profile/config.json', 'r') as f:
    data = json.load(f)
    tiles = data["tiles"]
    bounds = tuple(data["bounds"])

path = f"{sys.argv[1]}/data/"

paths = []
for tile in tiles:
    tile_id = tile[0:3]
    url = f"https://ftp.maps.canada.ca/pub/nrcan_rncan/elevation/cdem_mnec/{tile_id}/cdem_dem_{tile}_tif.zip"
    response = requests.get(url, stream=True)
    
    f_name = f"cdem_dem_{tile}_tif.zip"
    tiff_name = f"cdem_dem_{tile}.tif"
    os.makedirs(os.path.dirname(f"{path}raw/elevation/{f_name}"), exist_ok=True)
    with open(f"{path}raw/elevation/{f_name}", mode="wb") as f:
        for chunk in response.iter_content(chunk_size=10 * 1024):
            f.write(chunk)
    paths.append(f"{path}raw/elevation/{tiff_name}")
    if os.path.exists(paths[-1]):
        os.remove(paths[-1])
    os.system(f"unzip -no -d {path}raw/elevation/ {path}raw/elevation/{f_name}")
    os.system(f"rm -rf {path}raw/elevation/{f_name}")

merged_tiff = f"{path}raw/elevation/cdem_merged.tif"
if os.path.exists(merged_tiff):
    os.remove(merged_tiff)
ds = gdal.Warp(merged_tiff, paths, srcNodata=-32767, dstNodata=-32767, multithread=True)
ds = None
print(f"[LOG] Merged {len(paths)} tiffs")

d03_tiff = f"{path}raw/elevation/cdem_d03.tif"
if os.path.exists(d03_tiff):
    os.remove(d03_tiff)
ds = gdal.Warp(
    d03_tiff,
    merged_tiff,
    srcNodata=-32767,
    dstNodata=-32767,
    multithread=True,
    outputBounds=(bounds[0][0], bounds[0][1], bounds[1][0], bounds[1][1]),
)
ds = None
print(f"[LOG] Cropped to bounds {(bounds[0][0], bounds[0][1], bounds[1][0], bounds[1][1])}")

final_tiff = f"{path}raw/elevation/cdem_final.tif"
if os.path.exists(final_tiff):
    os.remove(final_tiff)
ds = gdal.Warp(
    final_tiff,
    d03_tiff,
    srcSRS="EPSG:4617",
    dstSRS="EPSG:4326",
    srcNodata=-32767,
    dstNodata=-32767,
    multithread=True,
    resampleAlg="bilinear",
)
ds = None
print(f"[LOG] Reprojected tiff")

ds = gdal.Open(final_tiff)
band = ds.GetRasterBand(1)
arr = band.ReadAsArray().astype(float)
nd = band.GetNoDataValue()
arr[arr == nd] = np.nan
bad_pct = 100 * np.isnan(arr).sum() / arr.size
print(f'  NoData value : {nd}')
print(f'  Valid min    : {np.nanmin(arr):.1f} m')
print(f'  Valid max    : {np.nanmax(arr):.1f} m')
print(f'  Valid mean   : {np.nanmean(arr):.1f} m')
print(f'  Bad pixels   : {bad_pct:.1f}%')
if bad_pct > 1.0:
    print(f'[ERROR] {bad_pct:.1f}% bad pixels — check tile coverage or clip bounds')
else:
    print(f'[LOG] Coverage looks clean')
    os.makedirs(os.path.dirname(f"{path}geog/elevation/ZSF"), exist_ok=True)
os.system(f"""{sys.argv[1]}/.libraries/wrfxpy/convert_geotiff.sh {final_tiff} {path}geog/ ZSF""")