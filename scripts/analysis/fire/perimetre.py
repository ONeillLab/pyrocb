import os
import json
import datetime
import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import imageio.v2 as imageio
from alpha_shapes.alpha_shapes import Alpha_Shaper

directory = "/scratch/su386/pyrocb2/out/output/complete/selkirk-2024-16"
analysis_dir = "/scratch/su386/pyrocb2/out/analysis/selkirk-2024-16"
gif_timestep = 1/6
gif_fps = 3

# --- Plot / grid config -------------------------------------------------------
SR = 7                  # fire subgrid ratio (sr_x / sr_y from the namelist)
WIND_LEVEL = 0           # vertical level index for wind quiver (0 = surface)
QUIVER_SKIP = 12         # quiver arrow density
tag = 'Fire perimeter (φ=0)'
linecolor = 'red'
NBAC = False             # no NBAC shapefile is wired into this script (see note below)


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
with open(f"{directory}/profile/config.json", 'r') as f:
    data = json.load(f)
    bounds = tuple(data["bounds"])
    name = data["name"]

wrfouts = {}
gdfs = []
for profile in os.scandir(f"{directory}/profile/satellite_detection_shapes"):
    if not profile.is_file or not profile.name.endswith(".shp"):
        continue
    data = os.path.join(profile.path)
    g = gpd.read_file(data)
    g["ACQ_DATETIME"] = g.apply(to_utc_dt, axis=1)
    gdfs.append(g)

gdf = gpd.GeoDataFrame(pd.concat(gdfs))

perimeter_output_path = f"{analysis_dir}/perimeter"
os.makedirs(perimeter_output_path, exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 8))
gdf.plot(ax=ax, color='lightblue', edgecolor='blue', alpha=0.5, zorder=1)
gdf.plot(ax=ax, color='red', markersize=20, zorder=2)
ax.set_title(f"satellite Detections from all {name} files")
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

if os.path.exists(f"{perimeter_output_path}/all_satellite_detections.png"):
    os.remove(f"{perimeter_output_path}/all_satellite_detections.png")
plt.savefig(f"{perimeter_output_path}/all_satellite_detections.png")
plt.close(fig)


def filter_bounds(gdf, bounds):
    gdf2 = gdf[gdf.LONGITUDE >= bounds[0][0]]
    gdf2 = gdf2[gdf2.LATITUDE <= bounds[0][1]]
    gdf2 = gdf2[gdf2.LONGITUDE <= bounds[1][0]]
    gdf2 = gdf2[gdf2.LATITUDE >= bounds[1][1]]
    return gdf2


gdf = filter_bounds(gdf, bounds)

fig, ax = plt.subplots(figsize=(8, 8))
gdf.plot(ax=ax, color='lightblue', edgecolor='blue', alpha=0.5, zorder=1)
gdf.plot(ax=ax, color='red', markersize=20, zorder=2)
ax.set_title(f"Cropped satellite Detections from {name}")
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

if os.path.exists(f"{perimeter_output_path}/satellite_detections_in_bounds.png"):
    os.remove(f"{perimeter_output_path}/satellite_detections_in_bounds.png")
plt.savefig(f"{perimeter_output_path}/satellite_detections_in_bounds.png")
plt.close(fig)

# --- Index available wrfout files by time -------------------------------------
format_string = '%Y-%m-%d_%H:%M:%S'
for out_file in os.scandir(directory):
    if not out_file.is_file():
        continue
    if not out_file.name.startswith("wrfout_d03"):
        continue
    time_str = out_file.name[len("wrfout_d03_"):]
    out_time = datetime.datetime.strptime(time_str, format_string).replace(tzinfo=datetime.timezone.utc)
    wrfouts[out_file.name] = out_time

start_time = min(wrfouts.values())
end_time = max(wrfouts.values())

# Grab TIGN_G once from the earliest wrfout to use as the ignition-timeline
# backdrop on the heat-flux panel (mirrors the `first_run` step in the
# comparison script).
earliest_file = min(wrfouts, key=wrfouts.get)
with Dataset(os.path.join(directory, earliest_file)) as ds0:
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

    most_recent_satellite_time = None
    g2 = gdf[gdf.ACQ_DATETIME <= current_time]
    if len(g2) > 0:
        most_recent_satellite_time = g2.ACQ_DATETIME.max()
        g2, window_start, window_end = filter_time(g2, most_recent_satellite_time, window=4)

    alpha_gdf = alpha_shape_from_points(g2)

    print(f"Frame: {current_time}, wrfout: {closest_wrfout[1]}, satellite: {most_recent_satellite_time}")

    with Dataset(os.path.join(directory, closest_wrfout[0])) as ds:
        # Atmospheric grid coords (degrees lat/lon for real data — NOT km)
        xlon = read_var(ds, 'XLONG')   # (south_north, west_east)
        xlat = read_var(ds, 'XLAT')

        # Fire subgrid coords
        xf = read_var(ds, 'FXLONG')    # (south_north_subgrid, west_east_subgrid)
        yf = read_var(ds, 'FXLAT')

        # Fire and terrain fields
        lfn = read_var(ds, 'LFN')      # level-set function
        hgt = read_var(ds, 'HGT')      # terrain height (atm grid)
        fhfx = read_var(ds, 'FGRNHFX')  # fire heat flux (fire grid)

        fig, axes = plt.subplots(1, 2, figsize=(18, 8))
        ax1, ax2 = axes

        # ── LEFT PANEL: terrain + fire perimeter + wind + satellite detections ──
        CS = ax1.contourf(xlon, xlat, hgt, levels=20, cmap='gray')
        cbar1 = plt.colorbar(CS, ax=ax1, pad=0.02)
        cbar1.set_label('Terrain height (m)')


        if len(g2) > 0:
            satellite_time = (most_recent_satellite_time - datetime.timedelta(hours = 1)).strftime("%d-%m %H:%M")
            satellites = ", ".join(list(set(g2.INSTRUMENT)))
            g2.plot(ax=ax1, color='green', markersize=5, alpha=0.5, zorder=3, label=f'satellite detections ({satellite_time} $\pm$ 01:00, {satellites})')

        if alpha_gdf is not None:
            alpha_gdf.plot(ax=ax1, facecolor='green', edgecolor='none', alpha=0.25, linewidth=1.5, zorder=2)
            alpha_gdf.plot(ax=ax1, edgecolor='lime', facecolor='none', alpha=0.85, linewidth=1.5, zorder=2)
            ax1.plot([], [], color='lime', label=f'satellite alpha-shape footprint ({satellite_time} $\pm$ 01:00, {satellites})')

        qv = wind_plot(ax1, ds, xlon, xlat, WIND_LEVEL, QUIVER_SKIP, color='white')
        plt.quiverkey(qv, 0.82, 0.95, U=10, label='10 m/s', labelpos='E', coordinates='figure', color='k')

        fire_perimeter_plot(ax1, xf, yf, lfn, color=linecolor, label=tag, zorder= 4)

        ax1.set_title('Terrain + fire perimeter + wind')
        ax1.set_xlabel('Longitude (°)')
        ax1.set_ylabel('Latitude (°)')
        ax1.legend(loc='upper left', fontsize=8)

        # ── RIGHT PANEL: fire heat flux + ignition timeline + satellite detections ──
        fhfx_c = relax_zone_remover(fhfx, SR)
        xf_c = relax_zone_remover(xf, SR)
        yf_c = relax_zone_remover(yf, SR)

        ignition_cs = ax2.contourf(xf_c, yf_c, ignition_masked, cmap='Purples', levels=8)
        ignition_cbar = plt.colorbar(ignition_cs, ax=ax2, pad=0.02)
        ignition_cbar.set_label('Ignition time (s)')

        if NBAC:
            nbac.to_crs('EPSG:4326').plot(color='purple', alpha=0.5, ax=ax2, label='NBAC perimeter')

        if len(g2) > 0:
            g2.plot(ax=ax2, color='green', markersize=5, alpha=0.5, zorder=3, label=f'satellite detections ({satellite_time} $\pm$ 01:00, {satellites})')

        if alpha_gdf is not None:
            alpha_gdf.plot(ax=ax2, edgecolor='lime', facecolor='none', alpha=0.25, linewidth=1.5, zorder=2)
            ax2.plot([], [], color='lime', label=f'satellite alpha-shape footprint ({satellite_time} $\pm$ 01:00, {satellites})')

        # Mask zeros so unburned area is transparent
        fhfx_masked = np.ma.masked_where(fhfx_c < 100, fhfx_c)  # threshold in W/m²
        CS2 = ax2.contourf(xf_c, yf_c, fhfx_masked, levels=20, cmap='copper_r', zorder= 4)
        cbar2 = plt.colorbar(CS2, ax=ax2, pad=0.02)
        cbar2.set_label('Ground fire heat flux (W/m²)')

        fire_perimeter_plot(ax2, xf, yf, lfn, color=linecolor, label=tag, zorder= 5)

        ax2.set_title('Fire heat flux (33 m subgrid)')
        ax2.set_xlabel('Longitude (°)')
        ax2.set_ylabel('Latitude (°)')
        ax2.legend(loc='upper left', fontsize=8)

        fig.suptitle(current_time.strftime(format_string))
        plt.tight_layout()
        frame_name = current_time.strftime("%Y%m%d-%H%M")
        frame_path = f"{perimeter_output_path}/fire_perimeter{frame_name}.png"
        plt.savefig(frame_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved_files.append(frame_path)

    i += 1
    current_time += datetime.timedelta(hours=gif_timestep)

print(f"Saved {i} frames to {perimeter_output_path}")

# --- Assemble the frames into a GIF -------------------------------------------
if len(saved_files) > 1:
    gif_path = f"{perimeter_output_path}/fire_perimeter_animation.gif"
    with imageio.get_writer(gif_path, mode='I', fps=gif_fps, loop=0) as writer:
        for fname in saved_files:
            writer.append_data(imageio.imread(fname))
    print(f'Saved animation: {gif_path}')
else:
    print('No frames were saved — skipping GIF creation.')