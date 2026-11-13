# Sylvio Dos Reis, 2026
# Plots the observed satellite fire perimeter and simulated fire perimeter by frame. Then combines each frame into a gif
import sys
_, utils_path, profile, analysis_path = sys.argv

import os
import json
import sys
import datetime
import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import imageio.v2 as imageio
from alpha_shapes.alpha_shapes import Alpha_Shaper
from wrf import getvar, to_np

sys.path.append(utils_path)
from geoutils import bound_expansion

print(profile)
analysis_dir = f"{analysis_path}{os.path.basename(profile)}"
print(analysis_dir)
gif_timestep = 1/6
gif_fps = 3

# --- Plot / grid config -------------------------------------------------------
SR = 7                  # fire subgrid ratio (sr_x / sr_y from the namelist)
WIND_LEVEL = 0           # vertical level index for wind quiver (0 = surface)
QUIVER_SKIP = 12         # quiver arrow density
tag = 'Fire perimeter (φ=0)'
linecolor = 'red'
NBAC = False             # no NBAC shapefile is wired into this script (see note below)
SMOKE_VAR = 'fire_smoke'
QC_THRESH = 1e-6
QC_LEVELS = np.linspace(QC_THRESH, 5e-3, 15)
QI_THRESH = 1e-5
QI_LEVELS = np.linspace(QI_THRESH, 1e-3, 15)  
SM_THRESH = 1e-6                               
SM_LEVELS = np.linspace(SM_THRESH, 1e-2, 15)   

def load_wrfout(data_dir, date_str):
    path = f'{data_dir}wrfout_d03_{date_str}'
    return Dataset(path)


def to_utc_dt(row):
    date_val = row['ACQ_DATE']
    date_str = date_val.split(' ')[0] if isinstance(date_val, str) else pd.Timestamp(date_val).strftime('%Y-%m-%d')
    time_num = str(int(row['ACQ_TIME'])).zfill(4)
    dt = datetime.datetime.strptime(date_str + time_num, '%Y-%m-%d%H%M')
    return dt.replace(tzinfo=datetime.timezone.utc)


def filter_time(gdf, time, window=2.0):
    start_time = time - datetime.timedelta(hours=window / 2)
    end_time = time + datetime.timedelta(hours=window / 2)
    gdf2 = gdf[gdf.ACQ_DATETIME >= start_time]
    gdf2 = gdf2[gdf2.ACQ_DATETIME <= end_time]
    return gdf2, start_time, end_time

def filter_confidence(gdf, confidence=30):
    start_time = time - datetime.timedelta(hours=window / 2)
    end_time = time + datetime.timedelta(hours=window / 2)
    gdf2 = gdf[gdf.ACQ_DATETIME >= start_time]
    gdf2 = gdf2[gdf2.ACQ_DATETIME <= end_time]
    return gdf2, start_time, end_time

def relax_zone_remover(arr, sr):
    return arr[sr:-sr, sr:-sr]


def fire_perimeter_plot(ax, xf, yf, lfn, color='red', zorder=1, label='Fire perimeter (φ=0)'):
    if label is None:
        label = 'Fire perimeter (φ=0)'
    lfn_c = relax_zone_remover(lfn, SR)
    xf_c = relax_zone_remover(xf, SR)
    yf_c = relax_zone_remover(yf, SR)
    ax.contour(xf_c, yf_c, lfn_c, levels=[0], colors=color, linewidths=1.5, zorder=zorder)
    ax.plot([], [], color=color, label=label)

def read_var(ds, name, timeidx=0):
    return np.array(ds.variables[name][timeidx])


def destagger(arr, axis):
    lo = np.take(arr, np.arange(arr.shape[axis] - 1), axis=axis)
    hi = np.take(arr, np.arange(1, arr.shape[axis]), axis=axis)
    return (lo + hi) / 2.0


def earth_relative_wind(ds, level, timeidx=0):
    u_stag = read_var(ds, 'U', timeidx)   # (bottom_top, south_north, west_east_stag)
    v_stag = read_var(ds, 'V', timeidx)   # (bottom_top, south_north_stag, west_east)
    u = destagger(u_stag, axis=2)[level]  # -> (south_north, west_east)
    v = destagger(v_stag, axis=1)[level]

    cosalpha = read_var(ds, 'COSALPHA', timeidx)
    sinalpha = read_var(ds, 'SINALPHA', timeidx)
    u_earth = u * cosalpha - v * sinalpha
    v_earth = u * sinalpha + v * cosalpha
    return u_earth, v_earth


def wind_plot(ax, data, xcoords, ycoords, level, quiver_skip, color='white'):
    u2d, v2d = earth_relative_wind(data, level)
    qv = ax.quiver(
        xcoords[::quiver_skip, ::quiver_skip], ycoords[::quiver_skip, ::quiver_skip],
        u2d[::quiver_skip, ::quiver_skip], v2d[::quiver_skip, ::quiver_skip],
        color=color, scale=300, scale_units='width',
        pivot='tail', width=0.002
    )
    return qv


def alpha_shape_from_points(points_gdf, min_points=4):
    if len(points_gdf) < min_points:
        return None
    points = np.array([(geom.x, geom.y) for geom in points_gdf.geometry])
    try:
        shaper = Alpha_Shaper(points)
        alpha_opt, alpha_shape = shaper.optimize()
    except Exception as e:
        print(f"Alpha shape fit failed ({len(points_gdf)} points): {e}")
        return None
    return gpd.GeoSeries([alpha_shape], crs=points_gdf.crs)


# --- Load config & satellite detections --------------------------------------
bounds = ()
with open(f"{profile}/profile/config.json", 'r') as f:
    data = json.load(f)
    bounds = tuple(data["bounds"])
with open(f"{profile}/profile/profile", 'r') as p:
    name = p.read().strip()
north, east, south, west = bound_expansion((bounds[0][1], bounds[0][0]), (bounds[1][1], bounds[1][0]))
print(f"North: {north}, East: {east}, South: {south}, West: {west}")
print(name)

wrfouts = {}

cloud_output_path = f"{analysis_dir}/atmosphere/cloud"
os.makedirs(cloud_output_path, exist_ok=True)

# --- Index available wrfout files by time -------------------------------------
format_string = '%Y-%m-%d_%H:%M:%S'
for out_file in os.scandir(f"{profile}"):
    if not out_file.is_file():
        continue
    if not out_file.name.startswith("wrfout_d03"):
        continue
    time_str = out_file.name[len("wrfout_d03_"):]
    out_time = datetime.datetime.strptime(time_str, format_string).replace(tzinfo=datetime.timezone.utc)
    wrfouts[out_file.path] = out_time
start_time = min(wrfouts.values())
end_time = max(wrfouts.values())

# Grab TIGN_G once from the earliest wrfout to use as the ignition-timeline
# backdrop on the heat-flux panel (mirrors the `first_run` step in the
# comparison script).
earliest_file = min(wrfouts, key=wrfouts.get)
with Dataset(os.path.join(profile, earliest_file)) as ds0:
    ignition = read_var(ds0, 'TIGN_G')
ignition = relax_zone_remover(ignition, SR)
ignition_masked = np.ma.masked_where(ignition >= 1e6, ignition)

# --- Main loop: one frame per gif_timestep ------------------------------------
current_time = start_time
i = 0
saved_files = []  # track filenames in order for the GIF
while current_time <= end_time:
    closest_wrfout = None
    for wname, wtime in wrfouts.items():
        if wtime <= current_time and (closest_wrfout is None or closest_wrfout[1] < wtime):
            closest_wrfout = (wname, wtime)

    if closest_wrfout is None:
        current_time += datetime.timedelta(hours=gif_timestep)
        continue

    print(f"Frame: {current_time}, wrfout: {closest_wrfout[1]}")

    with Dataset(os.path.join(profile, closest_wrfout[0])) as ds:
        # Atmospheric grid coords (degrees lat/lon for real data — NOT km)
        xlon = read_var(ds, 'XLONG')   # (south_north, west_east)
        xlat = read_var(ds, 'XLAT')

        # Fire subgrid coords
        xf = read_var(ds, 'FXLONG')    # (south_north_subgrid, west_east_subgrid)
        yf = read_var(ds, 'FXLAT')

        # Fire and terrain fields
        lfn = read_var(ds, 'LFN')      # level-set function
        hgt = read_var(ds, 'HGT')      # terrain height (atm grid)
        qcloud = to_np(getvar(ds, "QCLOUD").sum(dim="bottom_top"))
        qice   = to_np(getvar(ds, "QICE").sum(dim="bottom_top"))
        if "fire_smoke" in ds.variables:
            smoke = read_var(ds, "fire_smoke").sum(axis=0)
        elif "tr17_1" in ds.variables:
            smoke = read_var(ds, "tr17_1").sum(axis=0)
        else:
            smoke = np.zeros_like(qcloud)   # nothing to plot this frame

        print(f"max qcloud: {qcloud.max():.2e}  qice: {qice.max():.2e}  smoke: {smoke.max():.2e}")

        qcloud_m = np.ma.masked_where(qcloud < QC_THRESH, qcloud)
        qice_m   = np.ma.masked_where(qice   < QI_THRESH, qice)
        smoke_m  = np.ma.masked_where(smoke  < SM_THRESH, smoke)

        fig, axes = plt.subplots(1, 2, figsize=(18, 8))
        ax1, ax2 = axes

        # ── LEFT PANEL: terrain + fire perimeter + qcloud + qice ──
        CS = ax1.contourf(xlon, xlat, hgt, levels=20, cmap='gray')
        cbar1 = plt.colorbar(CS, ax=ax1, pad=0.02)
        cbar1.set_label('Terrain height (m)')

        fire_perimeter_plot(ax1, xf, yf, lfn, color=linecolor, label=tag, zorder= 4)

        CSq = ax1.contourf(xlon, xlat, qcloud_m, levels=QC_LEVELS, cmap='Blues', alpha=0.6, extend='max', zorder=2)
        cbarq = plt.colorbar(CSq, ax=ax1, pad=0.02)
        cbarq.set_label('QCLOUD summed over levels (kg/kg)')

        ax1.contour(xlon, xlat, qice_m, levels=QI_LEVELS, colors='plum', linewidths=0.8, zorder=3)
        ax1.plot([], [], color='plum', label='QICE (summed)')

        ax1.set_title('Terrain + fire perimeter + wind')
        ax1.set_xlabel('Longitude (°)')
        ax1.set_ylabel('Latitude (°)')
        ax1.legend(loc='upper left', fontsize=8)

        # ── RIGHT PANEL: smoke + qice + qcloud
        xf_c = relax_zone_remover(xf, SR)
        yf_c = relax_zone_remover(yf, SR)

        # ── RIGHT PANEL: qcloud + qice + fire smoke ──
        if qcloud_m.count() > 0:
            ax2.contour(xlon, xlat, qcloud_m, levels=QC_LEVELS, colors='cornflowerblue', linewidths=0.8, zorder=3)
            ax2.plot([], [], color='cornflowerblue', label='QCLOUD (summed)')

        if qice_m.count() > 0:
            ax2.contour(xlon, xlat, qice_m, levels=QI_LEVELS, colors='plum', linewidths=0.8, zorder=3)
            ax2.plot([], [], color='plum', label='QICE (summed)')

        if smoke_m.count() > 0:
            CSs = ax2.contourf(xlon, xlat, smoke_m, levels=SM_LEVELS, cmap='gray_r', alpha=0.6, extend='max', zorder=3)
            plt.colorbar(CSs, ax=ax2, pad=0.02, shrink=0.8).set_label('fire_smoke summed')

        fire_perimeter_plot(ax2, xf, yf, lfn, color=linecolor, label=tag, zorder=5)

        ax2.set_title('QCLOUD + QICE + fire smoke')
        ax2.set_xlabel('Longitude (°)')
        ax2.set_ylabel('Latitude (°)')
        ax2.legend(loc='upper left', fontsize=8)

        fig.suptitle(current_time.strftime(format_string))
        plt.tight_layout()
        frame_name = current_time.strftime("%Y%m%d-%H%M")
        frame_path = f"{cloud_output_path}/cloud_{frame_name}.png"
        plt.savefig(frame_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved_files.append(frame_path)

    i += 1
    current_time += datetime.timedelta(hours=gif_timestep)

print(f"Saved {i} frames to {cloud_output_path}")

# --- Assemble the frames into a GIF -------------------------------------------
if len(saved_files) > 1:
    gif_path = f"{cloud_output_path}/cloud_animation.gif"
    with imageio.get_writer(gif_path, mode='I', fps=gif_fps, loop=0) as writer:
        for fname in saved_files:
            writer.append_data(imageio.imread(fname))
    print(f'Saved animation: {gif_path}')
else:
    print('No frames were saved — skipping GIF creation.')