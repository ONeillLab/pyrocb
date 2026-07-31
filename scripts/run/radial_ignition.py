import datetime
import numpy as np
import pandas as pd
import os
import geopandas as gpd
from scipy.ndimage import distance_transform_edt
from netCDF4 import Dataset
import matplotlib.path as path
import matplotlib.pyplot as plt
import sys
import json
import f90nml
from shapely.geometry import Point
from shapely.ops import transform, unary_union
from pyproj import CRS, Transformer

bounds = ()

with open(f'{sys.argv[1]}/profile/config.json', 'r') as f:
    data = json.load(f)
    run_start_time_str = data["run_start_time"]
    ignition_start_time_str = data["ignition_start_time"]
    bounds = tuple(data["bounds"])
    name = data["name"]

format_string = '%Y-%m-%d_%H:%M:%S'
run_start_utc = datetime.datetime.strptime(run_start_time_str, format_string).replace(tzinfo=datetime.timezone.utc)
ignition_start_time = datetime.datetime.strptime(ignition_start_time_str, format_string).replace(tzinfo=datetime.timezone.utc)
wrfout_ref = "/path/to/wrfout_d03_ref"

wrfin = f"{sys.argv[1]}/output/{name}/real_em/wrfinput_d03"
namelist_file = f"{sys.argv[1]}/profile/namelist.input"

BUFFER_RADIUS_M = 375/2

def read_wrffile(var, fname):
    with Dataset(fname, 'r') as fnc:
        dat = fnc.variables[var][:]
        return np.squeeze(dat)


def write_wrffile(var, data, fname):
    with Dataset(fname, 'r+') as fnc:
        if len(fnc.variables[var].shape) == 3:
            fnc.variables[var][0, :, :] = data
        else:
            fnc.variables[var][:] = data


def to_utc_dt(row):
    date_val = row['ACQ_DATE']
    date_str = date_val.split(' ')[0] if isinstance(date_val, str) else pd.Timestamp(date_val).strftime('%Y-%m-%d')
    time_num = str(int(row['ACQ_TIME'])).zfill(4)
    dt = datetime.datetime.strptime(date_str + time_num, '%Y-%m-%d%H%M')
    return dt.replace(tzinfo=datetime.timezone.utc)


gdfs = []
for profile in os.scandir(f"{sys.argv[1]}/profile/satellite_detection_shapes"):
    if not profile.is_file or not profile.name.endswith(".shp"):
        continue
    data = os.path.join(profile.path)
    g = gpd.read_file(data)
    g["ACQ_DATETIME"] = g.apply(to_utc_dt, axis=1)
    gdfs.append(g)

gdf = gpd.GeoDataFrame(pd.concat(gdfs))

ignition_output_path = f"{sys.argv[1]}/output/{name}/ignition"
os.makedirs(ignition_output_path, exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 8))
gdf.plot(ax=ax, color='lightblue', edgecolor='blue', alpha=0.5, zorder=1)
gdf.plot(ax=ax, color='red', markersize=20, zorder=2)
ax.set_title(f"satellite Detections from all {name} files")
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

if os.path.exists(f"{ignition_output_path}/all_satellite_detections.png"):
    os.remove(f"{ignition_output_path}/all_satellite_detections.png")
plt.savefig(f"{ignition_output_path}/all_satellite_detections.png")


def filter_bounds(gdf, bounds):
    gdf2 = gdf[gdf.LONGITUDE >= bounds[0][0]]
    gdf2 = gdf2[gdf2.LATITUDE <= bounds[0][1]]
    gdf2 = gdf2[gdf2.LONGITUDE <= bounds[1][0]]
    gdf2 = gdf2[gdf2.LATITUDE >= bounds[1][1]]
    return gdf2


def filter_time(gdf, time, window=2.0):
    start_time = time - datetime.timedelta(hours=window / 2)
    end_time = time + datetime.timedelta(hours=window / 2)
    gdf2 = gdf[gdf.ACQ_DATETIME >= start_time]
    gdf2 = gdf2[gdf2.ACQ_DATETIME <= end_time]
    return gdf2, start_time, end_time


gdf = filter_bounds(gdf, bounds)

fig, ax = plt.subplots(figsize=(8, 8))
gdf.plot(ax=ax, color='lightblue', edgecolor='blue', alpha=0.5, zorder=1)
gdf.plot(ax=ax, color='red', markersize=20, zorder=2)
ax.set_title(f"Cropped satellite Detections from {name}")
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

if os.path.exists(f"{ignition_output_path}/satellite_detections_in_bounds.png"):
    os.remove(f"{ignition_output_path}/satellite_detections_in_bounds.png")
plt.savefig(f"{ignition_output_path}/satellite_detections_in_bounds.png")

ignition_time = gdf.ACQ_DATETIME.min()
print(f"Detected Ignition at {ignition_time}")

gdf, start_time, end_time = filter_time(gdf, ignition_time, window=3)
print(f"Selecting points between {start_time} and {end_time}")

points = np.array([(geom.x, geom.y) for geom in gdf.geometry])  # (lon, lat)

center_lon, center_lat = points[:, 0].mean(), points[:, 1].mean()
local_crs = CRS.from_proj4(
    f"+proj=aeqd +lat_0={center_lat} +lon_0={center_lon} +datum=WGS84 +units=m"
)
to_local = Transformer.from_crs("EPSG:4326", local_crs, always_xy=True)
to_lonlat = Transformer.from_crs(local_crs, "EPSG:4326", always_xy=True)

circles_local = []
for lon, lat in points:
    x, y = to_local.transform(lon, lat)
    circles_local.append(Point(x, y).buffer(BUFFER_RADIUS_M))

fire_shape_local = unary_union(circles_local)
fire_shape_lonlat = transform(lambda x, y: to_lonlat.transform(x, y), fire_shape_local)

# Preview the flattened (unioned) shape, reprojected to lon/lat, for the plot below
fire_gdf = gpd.GeoSeries([fire_shape_lonlat], crs=gdf.crs)

fig, ax = plt.subplots(figsize=(8, 8))
fire_gdf.plot(ax=ax, color='lightblue', edgecolor='blue', alpha=0.5, zorder=1)
gdf.plot(ax=ax, color='red', markersize=20, zorder=2)
ax.set_title(f"Fire area from {start_time} to {end_time}")
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_aspect(1 / np.cos(np.radians(center_lat)))

if os.path.exists(f"{ignition_output_path}/ignition_area.png"):
    os.remove(f"{ignition_output_path}/ignition_area.png")
plt.savefig(f"{ignition_output_path}/ignition_area.png")


tign = read_wrffile('TIGN_G', wrfin)
xlat = read_wrffile('XLAT', wrfin)
xlon = read_wrffile('XLONG', wrfin)

nml = f90nml.read(namelist_file)
dom = 2  # d03 (0=d01, 1=d02, 2=d03)
sr_x = nml["domains"]["sr_x"][dom]
sr_y = nml["domains"]["sr_y"][dom]
nx, ny = xlat.shape

fire_nx = nx * sr_x
fire_ny = ny * sr_y

lat_fire = np.empty((fire_ny, fire_nx))
lon_fire = np.empty((fire_ny, fire_nx))

for j in range(ny):
    for i in range(nx):
        if i != nx - 1:
            dlon = xlon[j, i + 1] - xlon[j, i]
            dylon = xlat[j, i + 1] - xlat[j, i]  # change in latitude moving one cell right
        if j != ny - 1:
            dlat = xlat[j + 1, i] - xlat[j, i]
            dxlat = xlon[j + 1, i] - xlon[j, i]  # change in longitude moving one cell down

        # Approximating box coordinates using differences between XLAT/XLON
        # (which represent the middle coordinates of the boxes).
        # Top edge
        top_left_lat = xlat[j, i] - dlat / 2 - dylon / 2
        top_left_lon = xlon[j, i] - dlon / 2 - dxlat / 2
        top_right_lat = xlat[j, i] - dlat / 2 + dylon / 2
        top_right_lon = xlon[j, i] + dlon / 2 - dxlat / 2

        # Bottom edge
        bottom_left_lat = xlat[j, i] + dlat / 2 - dylon / 2
        bottom_left_lon = xlon[j, i] - dlon / 2 + dxlat / 2
        bottom_right_lat = xlat[j, i] + dlat / 2 + dylon / 2
        bottom_right_lon = xlon[j, i] + dlon / 2 + dxlat / 2

        # Interpolate along top and bottom edges
        lat_top = np.linspace(top_left_lat, top_right_lat, sr_x)
        lat_bottom = np.linspace(bottom_left_lat, bottom_right_lat, sr_x)

        lon_top = np.linspace(top_left_lon, top_right_lon, sr_x)
        lon_bottom = np.linspace(bottom_left_lon, bottom_right_lon, sr_x)

        # Interpolate between top and bottom
        lat_block = np.array([
            np.linspace(lat_top[k], lat_bottom[k], sr_y)
            for k in range(sr_x)
        ]).T

        lon_block = np.array([
            np.linspace(lon_top[k], lon_bottom[k], sr_y)
            for k in range(sr_x)
        ]).T

        # Insert into fire grid
        js = j * sr_y
        is_ = i * sr_x

        lat_fire[js:js + sr_y, is_:is_ + sr_x] = lat_block
        lon_fire[js:js + sr_y, is_:is_ + sr_x] = lon_block

print("Top-left :", lat_fire[0, 0], lon_fire[0, 0])
print("Top-right:", lat_fire[0, -2], lon_fire[0, -1])
print("Bottom-left:", lat_fire[-1, 0], lon_fire[-1, 0])
print("Bottom-right:", lat_fire[-1, -1], lon_fire[-1, -1])


def rings_from_shape(geom):
    """
    Convert a Shapely Polygon/MultiPolygon (lon, lat order) into a list of
    (N, 2) [lon, lat] rings -- one per lobe -- for mask_perim.
    """
    if geom.geom_type == 'MultiPolygon':
        geoms = list(geom.geoms)
    else:
        geoms = [geom]
    return [np.array(g.exterior.coords) for g in geoms]


def mask_perim(perim, coords):
    """perim: (lon, lat) ring. coords: [lon_grid, lat_grid]."""
    lon, lat = coords
    mp = path.Path(perim, closed=True)
    pts = np.array((lon.flatten(), lat.flatten())).T
    mask = mp.contains_points(pts).reshape(lat.shape)
    return mask


print("Grid shapes -- lat_fire:", lat_fire.shape, "lon_fire:", lon_fire.shape, "TIGN_G:", tign.shape)
print("lat_fire range:", lat_fire.min(), lat_fire.max())
print("lon_fire range:", lon_fire.min(), lon_fire.max())

# Build rings + mask on the WRF fire grid -- keep ALL lobes, not just the largest
rings = rings_from_shape(fire_shape_lonlat)
coords = [lon_fire, lat_fire]

masks = [mask_perim(ring, coords) for ring in rings]
mask = np.logical_or.reduce(masks)

print(f"Mask pixel count: {mask.sum()}")

# Generate Gradual Growth Distance Matrix
interior_distances = distance_transform_edt(mask)
mask_vals = interior_distances[mask]

if len(mask_vals) > 0 and mask_vals.max() > mask_vals.min():
    normalized_depth = np.zeros_like(interior_distances)
    min_d, max_d = mask_vals.min(), mask_vals.max()
    normalized_depth[mask] = (interior_distances[mask] - min_d) / (max_d - min_d)
else:
    normalized_depth = np.zeros_like(interior_distances)

# Interpolate the Ignition Matrix Timeline
# t_start/t_end are seconds relative to run_start_utc
t_start = (ignition_start_time - run_start_utc).total_seconds()
t_end = (ignition_time - run_start_utc).total_seconds()

print(f"t_start = {t_start}s ({ignition_start_time})")
print(f"t_end   = {t_end}s ({ignition_time})")

gradual_growth_tign = t_end - (t_end - t_start) * normalized_depth

# Map values into TIGN_G layout and save
tign_new = np.full(tign.shape, 9.99e6)

# Ignore the last srx
valid = tign_new[:fire_ny, :fire_nx]
valid[mask] = gradual_growth_tign[mask]
tign_new[:fire_ny, :fire_nx] = valid

write_wrffile('TIGN_G', tign_new, wrfin)

print("\n[Success] Injected gradual growth timeline matrix into TIGN_G successfully!")
print(f"Ignition start: {valid[mask].min()}s | Edge target: {valid[mask].max()}s")