# Created by Noah Vaillant, Sylvio Dos Reis, 2026
# Plots the Hovmoller plot for a given run

import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib as mpl
import xarray as xr
from netCDF4 import Dataset
import matplotlib.ticker as mticker
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, timedelta, timezone
import imageio.v2 as imageio
import os
import shutil
import matplotlib.colors as mcolors
import sys

from wrf import to_np, getvar, CoordPair, vertcross, destagger
from matplotlib.cm import get_cmap
from netCDF4 import Dataset


#============================CONFIG==============================================================

directory = sys.argv[1]
print(directory)
analysis_dir = f"{sys.argv[2]}{os.path.basename(directory)}"
print(analysis_dir)
LONGITUDE = -117.9
ALTITUDE = 4000

CLOUD_THRESH = 5e-5
SMOKE_THRESH = 1e-2


def get_timesteps_wrfout(directory):
    wrfouts = {}
    format_string = '%Y-%m-%d_%H:%M:%S'
    for out_file in os.scandir(directory):
        if not out_file.is_file():
            continue
        if not out_file.name.startswith("wrfout_d03"):
            continue
        time_str = out_file.name[len("wrfout_d03_"):]
        out_time = datetime.strptime(time_str, format_string).replace(tzinfo=timezone.utc)
        wrfouts[out_file.path] = out_time
    return wrfouts

def relax_zone_remover(arr, sr):
    """Strip sr rows/cols from all edges of a 2D fire-grid array."""
    return arr[sr:-sr, sr:-sr]

def load_wrfout(data_dir, date_str):
    path = f'{data_dir}wrfout_d03_{date_str}'
    return Dataset(path)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def get_vorticity_2order(U, V, W, dx, dy): #second order central difference scheme
    #adapted from parveer (thanks to parveer)
    dx = dx
    dy = dy
    dz_levels = np.array([float(W.bottom_top[i] - W.bottom_top[i-1]) for i in range(1, len(W.bottom_top))])
    dz = np.zeros_like(W.values)
    for i in range(len(dz_levels)):
        dz[i,:,:] = dz_levels[i]
    # x-vorticity
    dWdy = (W.shift(south_north=-1) - W.shift(south_north=1)) / (2 * dy)
    dVdz = (V.shift(bottom_top=-1) - V.shift(bottom_top=1)) / (2 * dz)
    omg_x = (dWdy - dVdz).fillna(0)

    # y-vorticity
    dUdz = (U.shift(bottom_top=-1) - U.shift(bottom_top=1)) / (2 * dz)
    dWdx = (W.shift(west_east=-1) - W.shift(west_east=1)) / (2 * dx)
    omg_y = (dUdz - dWdx).fillna(0)

    # z-vorticity
    dVdx = (V.shift(south_north=-1) - V.shift(south_north=1)) / (2 * dx)
    dUdy = (U.shift(west_east=-1) - U.shift(west_east=1)) / (2 * dy)
    omg_z = (dVdx - dUdy).fillna(0)

    return omg_x, omg_y, omg_z


def get_vars(data_dir, date_str):


    ds = load_wrfout(DATA_DIR, date_str)
    qice = getvar(ds, 'QICE')
    qcloud = getvar(ds, 'QCLOUD')
    u = getvar(ds, 'U')
    v = getvar(ds, 'V')
    w = getvar(ds, 'W')
    z = getvar(ds, "z")
    theta = getvar(ds, "theta")
    tracer =  getvar(ds, "tr17_6")

    u_destag = destagger(u,  stagger_dim=u.get_axis_num("west_east_stag"), meta=True)
    v_destag = destagger(v,  stagger_dim=v.get_axis_num("south_north_stag"), meta=True)
    w_destag = destagger(w,  stagger_dim=w.get_axis_num("bottom_top_stag"), meta=True)
    return qice, qcloud, u, v, w, z, theta, tracer, u_destag, v_destag, w_destag

def hovmoller_3d(wrfouts, voi, lat=None, lon=None, altitude=None, name="hovmollerplot"):
    if (lat is None) and (lon is None):
        print('FAIL!!! Lat and lon are both none')
        return None
    
    fig, ax = plt.subplots(1, 1, figsize=(16,9))
    data = []
    xaxis = []
    xlab = 'FAIL'
    yaxis = []
    ylab = 'Datetime'
    if altitude is None:
        print('Fail!, no z value for 3d voi')
        return None

    lon_index = []
    lat_index = []
    z_index = []

    file_names = list(wrfouts.keys())
    file_names.sort()
    min_dt = wrfouts[file_names[0]]
    max_dt = wrfouts[file_names[-1]]

    data = np.zeros([len(wrfouts), 300])
    data = np.where(data==0, np.nan, data)
    step_num = 0

    
    if voi == 'vertical velocity':
            title ='Vertical Velocity at z =  ' + str(altitude) + ' [m], Longitude = ' + str(lon) + ' [degrees]'
            cblabel='Vertical Velocity (m/s)'
            cblevels=[-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3]
            cmap='coolwarm'
    elif voi == 'cloud':
            title ='(Ice + Cloud Water) ratio at z =  ' + str(altitude) + ' [m], Longitude = ' + str(lon) + ' [degrees]'
            cblabel='Cloud and Ice Quantity (kg/kg)'
            cblevels=[1e-6, 5e-5, 10e-5,15e-5,20e-5,25e-5,30e-5]
            cmap='inferno'


    for f in file_names:
        ds = Dataset(f"{f}")
        current_dt = wrfouts[f]
        yaxis.append(str(current_dt))
    
        xlon = getvar(ds, 'XLONG')
        xlat = getvar(ds, 'XLAT')
        z = getvar(ds, 'z')

        if voi == 'cloud':
            qice = getvar(ds, 'QICE')
            qcloud = getvar(ds, 'QCLOUD')
            data_array = qice + qcloud


        if voi == 'vertical velocity':
            data_array = getvar(ds, 'W')

        if current_dt == min_dt:
            if lat is None:
                xlab= 'Latitude'
                for i in range(xlat.shape[0]):
                    lonidx = np.argmin(np.abs(xlon.values[i,:].flatten()-lon))
                    altidx = np.argmin(np.abs(z.values[:,i,lonidx].flatten()-altitude))
                    data[step_num, :] =  data_array.values[altidx,i,lonidx]
                    xaxis.append(xlat[i,lonidx])
                    lon_index.append(lonidx)
                    z_index.append(altidx)
                    lat_index.append(i)
            
            if lon is None:
                xlab= 'Longitude'
                for i in range(xlat.shape[0]):
                    latidx =  np.argmin(np.abs(xlat.values[:,i].flatten()-lat))
                    altidx = np.argmin(np.abs(z.values[:,latidx,i].flatten()-altitude))
                    data[step_num, :] = data_array.values[altidx,latidx,i]
                    xaxis.append(xlon[latidx,i])
                    lon_index.append(i)
                    z_index.append(altidx)
                    lat_index.append(latidx)

        else:
            data[step_num, :] = data_array.values[np.array(z_index),np.array(lat_index),np.array(lon_index)]
        step_num += 1

    data = data[~np.isnan(data).all(axis=1),:]

    num_colors = len(cblevels) + 1
    cmap = plt.colormaps[cmap].resampled(num_colors)
    norm = mcolors.BoundaryNorm(cblevels, cmap.N, extend='both')
    plt.imshow(data, cmap=cmap, norm=norm)

    if lon is None:
        plt.text(10, 10, 'Latitude = ' + str(lat1) + '-' + str(lat2) + ' (avg)',
                    ha='left', va='bottom',
                    fontsize=16, color='blue')

    plt.yticks(ticks=np.arange(0, data.shape[0], data.shape[0]//len(ax.get_yticks())), labels=np.array(yaxis)[np.arange(0, data.shape[0], data.shape[0]//len(ax.get_yticks()))])
    plt.xlabel(xlab)
    plt.xticks(ticks=np.arange(0, data.shape[1], data.shape[1]//len(ax.get_xticks())), labels=np.array(xaxis)[np.arange(0, data.shape[1], data.shape[1]//len(ax.get_xticks()))].round(2))
    plt.ylabel(ylab)
    plt.colorbar(label=cblabel, ticks=cblevels, shrink=0.6)
    plt.title(title)
    plt.tight_layout()
    print(name, 'done')
    plt.savefig(name)

def hovmoller_2d(wrfouts, voi, lat=None, lon=None, name="hovmollerplot"):
    if (lat is None) and (lon is None):
        print('FAIL!!! Lat and lon are both none')
        return None
    
    fig, ax = plt.subplots(1, 1, figsize=(16,9))
    data = []
    xaxis = []
    xlab = 'FAIL'
    yaxis = []
    ylab = 'Datetime'

    lon_index = []
    lat_index = []

    file_names = list(wrfouts.keys())
    file_names.sort()
    min_dt = wrfouts[file_names[0]]
    max_dt = wrfouts[file_names[-1]]

    data = np.zeros([len(wrfouts), 300])
    data = np.where(data==0, np.nan, data)
    step_num = 0

    
    if voi =='cloudtop':
        title ='Cloud Top Height'
        cblabel='Height (m)'
        cblevels=[1000,3000,5000,7000,9000,11000]
        cmap='inferno'
        
    if voi=='smoke injection':
        title ='Smoke Injection Height'
        cblabel='Height (m)'
        cmap='inferno'
        cblevels=[1000,3000,5000,7000,9000,11000,13000]

    for f in file_names:
        ds = Dataset(f"{f}")
        current_dt = wrfouts[f]
        yaxis.append(str(current_dt))
    
        xlon = getvar(ds, 'XLONG')
        xlat = getvar(ds, 'XLAT')
        z = getvar(ds, 'z')

        if voi=='cloudtop':
            qice = getvar(ds, 'QICE')
            qcloud = getvar(ds, 'QCLOUD')
        
            cloud_total = qice + qcloud
            cloudtop = cloud_total[0,:,:] -  cloud_total[0,:,:]
            cloudtop_array = cloudtop.values

            for i in range(qice.shape[0]):
                cloudmask = (cloud_total[i,:,:] >= CLOUD_THRESH)
                cloudtop_array[cloudmask] = z.values[i,:,:][cloudmask]

            cloudtop.values = cloudtop_array
            data_array = cloudtop

        if voi == 'smoke injection':
            tracer = getvar(ds, "tr17_6")
            smoketop = tracer[0,:,:] -  tracer[0,:,:]
            smoketop_array = smoketop.values
            for i in range(tracer.shape[0]):
                cloudmask = (tracer[i,:,:] >= SMOKE_THRESH)
                smoketop_array[cloudmask] = z.values[i,:,:][cloudmask]
            smoketop.values = smoketop_array
            data_array = smoketop
        
        if current_dt == min_dt:
            if lat is None:
                xlab= 'Latitude'
                for i in range(xlat.shape[0]):
                    lonidx = np.argmin(np.abs(xlon.values[i,:].flatten()-lon))
                    data[step_num, :] =  data_array.values[i,lonidx]
                    xaxis.append(xlat[i,lonidx])
                    lon_index.append(lonidx)
                    lat_index.append(i)

            if lon is None:
                xlab= 'Longitude'
                for i in range(xlat.shape[0]):
                    latidx =  np.argmin(np.abs(xlat.values[:,i].flatten()-lat))
                    data[step_num, :] = data_array.values[latidx,i]
                    xaxis.append(xlon[latidx,i])
                    lon_index.append(i)
                    lat_index.append(latidx)

        else:
            data[step_num, :] = data_array.values[np.array(lat_index),np.array(lon_index)]
        step_num += 1

    data = data[~np.isnan(data).all(axis=1),:]
    num_colors = len(cblevels) + 1
    cmap = plt.colormaps[cmap].resampled(num_colors)
    norm = mcolors.BoundaryNorm(cblevels, cmap.N, extend='both')
    plt.imshow(data, cmap=cmap, norm=norm)

    if lon is None:
        plt.text(10, 10, 'Latitude = ' + str(lat1) + '-' + str(lat2) + ' (avg)',
                    ha='left', va='bottom',
                    fontsize=16, color='blue')

    plt.yticks(ticks=np.arange(0, data.shape[0], data.shape[0]//len(ax.get_yticks())), labels=np.array(yaxis)[np.arange(0, data.shape[0], data.shape[0]//len(ax.get_yticks()))])
    plt.xlabel(xlab)
    plt.xticks(ticks=np.arange(0, data.shape[1], data.shape[1]//len(ax.get_xticks())), labels=np.array(xaxis)[np.arange(0, data.shape[1], data.shape[1]//len(ax.get_xticks()))].round(2))
    plt.ylabel(ylab)
    plt.colorbar(label=cblabel, ticks=cblevels, shrink=0.6)
    plt.title(title)
    plt.tight_layout()
    print(f"Saving {name}")
    plt.savefig(name)


wrfouts = get_timesteps_wrfout(directory)
for i in ['cloud', 'vertical velocity']:
    os.makedirs(f"{analysis_dir}/hovmoller/{i}/", exist_ok=True)
    hovmoller_3d(wrfouts, i, altitude=ALTITUDE, lon=LONGITUDE, name=f'{analysis_dir}/hovmoller/{i}/hovmoller_plot_lon{LONGITUDE}_alt{ALTITUDE}.png')

for i in ['cloudtop', 'smoke injection']:
    os.makedirs(f"{analysis_dir}/hovmoller/{i}/", exist_ok=True)
    hovmoller_2d(wrfouts, i, lon=LONGITUDE, name=f'{analysis_dir}/hovmoller/{i}/hovmoller_plot_lon{LONGITUDE}.png')
