import json
import os
import sys
import requests
import subprocess
from osgeo import gdal
import numpy as np

bounds = ()
tiles = []
time = {}


with open(f'{sys.argv[1]}/profile/config.json', 'r') as f:
    data = json.load(f)
    tiles = data["tiles"]

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
    os.remove(paths[-1])
    os.system(f"unzip -n -d {path}raw/elevation/ {path}raw/elevation/{f_name}")
    os.system(f"rm -rf {path}raw/elevation/{f_name}")

gdal.Warp(
    f"{path}raw/elevation/cdem_merged.tif",
    paths,
    srcNodata = -32767,
    dstNodata = -32767
)

os.remove(f"{path}raw/elevation/cdem_final.tif")
gdal.Warp(
    f"{path}raw/elevation/cdem_d03.tif",
    f"{path}raw/elevation/cdem_final.tif",
    srcSRS = "EPSG:4617",
    dstSRS = "EPSG:4236",
    srcNodata = -32767,
    dstNodata = -32767,
    multithread = True,
    resampleAlg="bilinear"
)

ds = gdal.Open(f'{path}raw/elevation/cdem_final.tif')
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
    print(f'  WARNING: {bad_pct:.1f}% bad pixels — check tile coverage or clip bounds')
else:
    print(f'  OK: coverage looks clean')
    os.makedirs(os.path.dirname(f"{path}geog/elevation/ZSF"), exist_ok=True)
os.system(f"""{sys.argv[1]}/wrfxpy/convert_geotiff.sh ${sys.argv[1]}/cdem_final.tif {path}geog/elevation ZSF""")