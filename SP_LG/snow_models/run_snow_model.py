import os
import numpy as np
from snow_models.snowpack.snowpack import run_snowpack
from snow_models.simple_models import simple_model
import subprocess
from make_met_forcing.ERA5_utils import lonlat_to_xy
import xarray as xr
import psutil
from scipy import spatial
import time


def run_model(my_track,
              config):

    my_track.init_vals = get_init_vals(my_track.info['start_date'],
                                    my_track.info['start_coords'],
                                    aux_dir=config.aux_data_dir)

    start_timer = time.time()

    if config.model_name == 'snowpack':

        my_track = run_snowpack(my_track,
                                       config)

    elif (config.model_name == 'degree_days') or (config.model_name == 'nesosim'):

        my_track = simple_model(my_track.met_forcing)

    end_timer = time.time()

    my_track.duration = int(end_timer-start_timer)

    return(my_track)


def get_init_vals(start_date,
                  start_loc,
                  aux_dir):

    if start_date.month == 8: # If ice parcel exists at start of simulation, then take W99 or

        pio_data = get_pio_field(start_date.year,start_date.month, pio_dir=aux_dir)

        w99_thick_field = get_w99_field(start_date.year,10,w99_dir=aux_dir)['depth']

        pio_thick_field = pio_data['thickness']

        lon_grid, lat_grid = np.array(pio_data['lon']), np.array(pio_data['lat'])
        x_grid, y_grid = lonlat_to_xy(lon_grid, lat_grid)
        xy_grid_points = list(zip(x_grid.ravel(), y_grid.ravel()))
        EASE_tree = spatial.KDTree(xy_grid_points)
        distance, index = EASE_tree.query(start_loc)
        nearest_index = np.unravel_index(index, (361, 361))
        pio_thick_point, w99_thick_point = pio_thick_field[nearest_index], w99_thick_field[nearest_index]

        if (np.isnan(w99_thick_point)) or (w99_thick_point < 0.01):

            w99_thick_point = 0.01
    else:

        pio_thick_point, w99_thick_point = 0.15, 0.01

    # return(pio_thick_point, w99_thick_point)
    return(pio_thick_point, 0.01)

def get_w99_field(year,month,w99_dir):

    with xr.open_dataset(f'{w99_dir}/{year}_mW99.nc') as data:
        ds_month = data.where(int(month) == data.month, drop=True)
        field = np.array(ds_month['depth'])[0]
        lon = ds_month['lon']
        lat = ds_month['lat']

    return({'depth':field,
            'lon':lon,
            'lat':lat})


def get_pio_field(year, month, pio_dir):
    with xr.open_dataset(f'{pio_dir}/pio_{year}.nc') as data:
        ds_month = data.where(int(month) == data.month, drop=True)
        field = np.array(ds_month['thickness'])[0]
        lon = ds_month['lon']
        lat = ds_month['lat']

    return ({'thickness': field,
             'lon': lon,
             'lat': lat})