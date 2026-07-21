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

files = []
for tile in tiles:
    tile_id = tile[0:3]
    url = f"https://ftp.maps.canada.ca/pub/nrcan_rncan/elevation/cdem_mnec/{tile_id}/cdem_dem_{tile}_tif.zip"
    response = requests.get(url, stream=True)
    
    f_name = f"cdem_dem_{tile}_tif.zip"
    tiff_name = f"cdem_dem_{tile}*.tif"
    os.makedirs(os.path.dirname(f"{path}raw/elevation/{f_name}"), exist_ok=True)
    with open(f"{path}raw/elevation/{f_name}", mode="wb") as f:
        for chunk in response.iter_content(chunk_size=10 * 1024):
            f.write(chunk)
    files.append(tiff_name)
    os.system(f"unzip -n -d {path}raw/elevation/ {path}raw/elevation/{f_name}")
    os.system(f"rm -rf {path}raw/elevation/{f_name}")

cmd = "-overwrite \\\n-srcnodata -32767 \\\n-dstnodata -32767 \\\n"

for f in files:
    cmd += f"{path}raw/elevation/{f} \\\n"
cmd += f"{path}raw/elevation/cdem_merged.tif"
os.system(cmd)
os.system(f"""gdalwarp -overwrite \\
    -s_srs EPSG:4617 \\
    -t_srs EPSG:4326 \\
    -srcnodata -32767 \\
    -dstnodata -32767 \\
    -r bilinear \\
    {path}raw/elevation/cdem_d03.tif {path}raw/elevation/cdem_final.tif""")

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